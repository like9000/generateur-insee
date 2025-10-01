from __future__ import annotations

import asyncio
from typing import Any, Optional

import httpx
from sqlmodel import Session, select

from ..config import Settings, get_settings
from ..models import Establishment


class GeocodingService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._client = httpx.AsyncClient(base_url=self.settings.ban_base_url)

    async def close(self) -> None:
        await self._client.aclose()

    async def geocode(self, address: str, city: str | None = None) -> Optional[dict[str, Any]]:
        params = {"q": address, "limit": 1}
        if city:
            params["city"] = city
        response = await self._client.get("/search/", params=params)
        response.raise_for_status()
        data = response.json()
        features = data.get("features", [])
        if not features:
            return None
        return features[0]

    async def geocode_establishment(self, session: Session, establishment: Establishment) -> None:
        if not establishment.address:
            return
        feature = await self.geocode(establishment.address, establishment.city)
        if not feature:
            establishment.geo_status = "not_found"
        else:
            geometry = feature.get("geometry", {})
            coordinates = geometry.get("coordinates", [None, None])
            establishment.geo_lon = coordinates[0]
            establishment.geo_lat = coordinates[1]
            establishment.geo_status = feature.get("properties", {}).get("score")
        session.add(establishment)
        session.commit()

    async def geocode_site(self, session: Session, site_id: int, limit: int = 100) -> int:
        statement = (
            select(Establishment)
            .where(Establishment.site_id == site_id)
            .where(Establishment.geo_lat.is_(None))
            .where(Establishment.address.is_not(None))
            .limit(limit)
        )
        to_geocode = session.exec(statement).all()
        count = 0
        for establishment in to_geocode:
            await self.geocode_establishment(session, establishment)
            count += 1
            await asyncio.sleep(0)  # yield control for cooperative multitasking
        return count


async def geocode_in_background(
    session_factory,
    site_id: int,
    chunk_size: int = 50,
    delay_seconds: int = 1,
) -> None:
    service = GeocodingService()
    try:
        while True:
            with session_factory() as session:
                processed = await service.geocode_site(session, site_id, limit=chunk_size)
            if processed == 0:
                break
            await asyncio.sleep(delay_seconds)
    finally:
        await service.close()
