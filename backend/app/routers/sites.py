from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..dependencies import get_db_session
from ..models import Site
from ..schemas import SiteCreate, SiteRead

router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("/", response_model=List[SiteRead])
def list_sites(session: Session = Depends(get_db_session)) -> List[Site]:
    return session.exec(select(Site)).all()


@router.post("/", response_model=SiteRead, status_code=status.HTTP_201_CREATED)
def create_site(payload: SiteCreate, session: Session = Depends(get_db_session)) -> Site:
    site = Site(**payload.dict())
    session.add(site)
    session.commit()
    session.refresh(site)
    return site


@router.get("/{site_id}", response_model=SiteRead)
def get_site(site_id: int, session: Session = Depends(get_db_session)) -> Site:
    site = session.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site introuvable")
    return site


@router.put("/{site_id}", response_model=SiteRead)
def update_site(site_id: int, payload: SiteCreate, session: Session = Depends(get_db_session)) -> Site:
    site = session.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site introuvable")
    for key, value in payload.dict().items():
        setattr(site, key, value)
    session.add(site)
    session.commit()
    session.refresh(site)
    return site


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_site(site_id: int, session: Session = Depends(get_db_session)) -> None:
    site = session.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site introuvable")
    session.delete(site)
    session.commit()
