from __future__ import annotations

import asyncio
from collections import deque
from datetime import datetime
from typing import Any, AsyncIterator, Optional

import httpx
from sqlmodel import Session, select
from tenacity import RetryError, retry, stop_after_attempt, wait_exponential

from ..config import Settings, get_settings
from ..models import Establishment, ImportJob, Site


class RateLimiter:
    def __init__(self, limit: int, period_seconds: int = 60) -> None:
        self.limit = limit
        self.period = period_seconds
        self.calls: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            loop = asyncio.get_event_loop()
            while True:
                now = loop.time()
                while self.calls and now - self.calls[0] > self.period:
                    self.calls.popleft()
                if len(self.calls) < self.limit:
                    self.calls.append(loop.time())
                    return
                wait_time = self.period - (now - self.calls[0])
                await asyncio.sleep(max(wait_time, 0))


class SireneClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._token: Optional[str] = None
        self._client = httpx.AsyncClient(
            base_url=self.settings.sirene_base_url,
            timeout=httpx.Timeout(30.0, read=30.0, write=30.0, connect=10.0),
        )
        self.rate_limiter = RateLimiter(self.settings.sirene_rate_limit_per_minute)

    async def close(self) -> None:
        await self._client.aclose()

    async def _get_auth_headers(self) -> dict[str, str]:
        if self.settings.sirene_api_key:
            return {"Authorization": f"Bearer {self.settings.sirene_api_key}"}
        if self.settings.sirene_oauth_client_id and self.settings.sirene_oauth_client_secret:
            if not self._token:
                await self._authenticate()
            return {"Authorization": f"Bearer {self._token}"}
        raise RuntimeError("Aucune méthode d'authentification SIRENE configurée")

    async def _authenticate(self) -> None:
        auth = httpx.BasicAuth(
            self.settings.sirene_oauth_client_id or "",
            self.settings.sirene_oauth_client_secret or "",
        )
        token_resp = await self._client.post(
            "https://api.insee.fr/token",
            data={"grant_type": "client_credentials"},
            auth=auth,
        )
        token_resp.raise_for_status()
        payload = token_resp.json()
        self._token = payload["access_token"]

    @retry(wait=wait_exponential(multiplier=1, min=1, max=30), stop=stop_after_attempt(3))
    async def _get(self, path: str, params: dict[str, Any]) -> httpx.Response:
        await self.rate_limiter.acquire()
        headers = await self._get_auth_headers()
        response = await self._client.get(path, headers=headers, params=params)
        if response.status_code == 429:
            raise httpx.HTTPStatusError("Rate limit", request=response.request, response=response)
        response.raise_for_status()
        return response

    async def iter_establishments(
        self,
        filters: dict[str, Any],
        page_size: int | None = None,
        start_cursor: str | None = None,
    ) -> AsyncIterator[tuple[list[dict[str, Any]], Optional[str]]]:
        cursor = start_cursor or "*"
        while cursor:
            params = {"nombre": page_size or self.settings.sirene_default_page_size, "curseur": cursor}
            params.update(filters)
            try:
                response = await self._get("/etablissements", params=params)
            except RetryError as exc:  # pragma: no cover - safety
                raise exc.last_attempt.exception()  # type: ignore[misc]
            payload = response.json()
            etablissements = payload.get("etablissements", [])
            next_cursor = payload.get("curseurSuivant")
            yield etablissements, next_cursor
            if not next_cursor or next_cursor == cursor:
                break
            cursor = next_cursor


class SireneImporter:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.client = SireneClient(self.settings)

    async def import_for_site(self, session: Session, job: ImportJob) -> ImportJob:
        site = session.get(Site, job.site_id)
        if not site:
            raise ValueError("Site introuvable")

        filters = self._build_filters(site, job)
        job.status = "running"
        job.updated_at = datetime.utcnow()
        session.add(job)
        session.commit()
        session.refresh(job)

        total_imported = job.total_imported
        total_closed = job.total_closed
        total_errors = job.total_errors

        try:
            async for etablissements, cursor in self.client.iter_establishments(
                filters=filters, start_cursor=job.cursor
            ):
                for etablissement in etablissements:
                    try:
                        imported, closed = self._upsert_establishment(session, site.id, etablissement)
                        total_imported += imported
                        total_closed += closed
                    except Exception as exc:  # pragma: no cover - logging placeholder
                        total_errors += 1
                        job.last_error = str(exc)
                session.commit()
                job.cursor = cursor
                job.total_imported = total_imported
                job.total_closed = total_closed
                job.total_errors = total_errors
                job.updated_at = datetime.utcnow()
                session.add(job)
                session.commit()
                if not cursor:
                    break

            job.status = "completed"
            job.updated_at = datetime.utcnow()
            session.add(job)
            session.commit()
            return job
        except Exception as exc:
            job.status = "failed"
            job.last_error = str(exc)
            job.updated_at = datetime.utcnow()
            session.add(job)
            session.commit()
            raise
        finally:
            await self.client.close()

    def _build_filters(self, site: Site, job: ImportJob) -> dict[str, Any]:
        filters: dict[str, Any] = {
            "statutDiffusion": "O",
            "etatAdministratifEtablissement": "A,B,F",
        }
        sirene_filters = site.sirene_filters or {}
        for key in ["codeNaf", "codePostalEtablissement", "codeCommuneEtablissement", "codeDepartementEtablissement"]:
            if value := sirene_filters.get(key):
                filters[key] = value
        if job.naf_code:
            filters["codeNaf"] = job.naf_code
        if job.department:
            filters["codeDepartementEtablissement"] = job.department
        if job.city:
            filters["codeCommuneEtablissement"] = job.city
        return filters

    def _upsert_establishment(self, session: Session, site_id: int, payload: dict[str, Any]) -> tuple[int, int]:
        siret = payload.get("siret")
        if not siret:
            raise ValueError("SIRET manquant")
        etablissements = payload.get("periodesEtablissement", [])
        current = etablissements[-1] if etablissements else {}

        address_parts = [
            current.get("numeroVoieEtablissement"),
            current.get("indiceRepetitionEtablissement"),
            current.get("typeVoieEtablissement"),
            current.get("libelleVoieEtablissement"),
        ]
        address = " ".join(str(part) for part in address_parts if part).strip() or None

        db_establishment = session.exec(
            select(Establishment).where(Establishment.siret == siret, Establishment.site_id == site_id)
        ).one_or_none()

        is_active = payload.get("etatAdministratifEtablissement", "A") == "A"
        closure_label = None if is_active else "Définitivement fermé"

        metadata = {
            "trancheEffectifs": payload.get("trancheEffectifsEtablissement"),
            "dateCreation": payload.get("dateCreationEtablissement"),
        }

        if db_establishment:
            db_establishment.business_name = payload.get("uniteLegale", {}).get("denominationUniteLegale")
            db_establishment.naf_code = payload.get("activitePrincipaleEtablissement")
            db_establishment.naf_label = payload.get("nomenclatureActivitePrincipaleEtablissement")
            db_establishment.address = address
            db_establishment.postal_code = current.get("codePostalEtablissement")
            db_establishment.city = current.get("libelleCommuneEtablissement")
            db_establishment.department = current.get("codeDepartementEtablissement")
            db_establishment.is_active = is_active
            db_establishment.closure_label = closure_label
            db_establishment.last_seen_at = datetime.utcnow()
            db_establishment.extra_metadata = metadata
            session.add(db_establishment)
            imported = 0
        else:
            db_establishment = Establishment(
                site_id=site_id,
                siren=payload.get("siren"),
                nic=payload.get("nic"),
                siret=siret,
                business_name=payload.get("uniteLegale", {}).get("denominationUniteLegale"),
                naf_code=payload.get("activitePrincipaleEtablissement"),
                naf_label=payload.get("nomenclatureActivitePrincipaleEtablissement"),
                address=address,
                postal_code=current.get("codePostalEtablissement"),
                city=current.get("libelleCommuneEtablissement"),
                department=current.get("codeDepartementEtablissement"),
                is_active=is_active,
                closure_label=closure_label,
                extra_metadata=metadata,
            )
            session.add(db_establishment)
            imported = 1

        closed = 1 if not is_active else 0
        return imported, closed
