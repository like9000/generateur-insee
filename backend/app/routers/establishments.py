from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..dependencies import get_db_session
from ..models import Establishment, Site
from ..schemas import EstablishmentRead

router = APIRouter(prefix="/sites/{site_id}/establishments", tags=["establishments"])


def _get_site(session: Session, site_id: int) -> Site:
    site = session.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site introuvable")
    return site


@router.get("/", response_model=List[EstablishmentRead])
def list_establishments(
    site_id: int,
    active: Optional[bool] = Query(default=None),
    postal_code: Optional[str] = Query(default=None),
    session: Session = Depends(get_db_session),
) -> List[Establishment]:
    _get_site(session, site_id)
    query = select(Establishment).where(Establishment.site_id == site_id)
    if active is not None:
        query = query.where(Establishment.is_active == active)
    if postal_code:
        query = query.where(Establishment.postal_code == postal_code)
    return session.exec(query).all()
