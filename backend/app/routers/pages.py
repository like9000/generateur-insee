from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..dependencies import get_db_session
from ..models import ManualPage, Site
from ..schemas import ManualPageCreate, ManualPageRead, ManualPageUpdate

router = APIRouter(prefix="/sites/{site_id}/pages", tags=["pages"])


def _get_site(session: Session, site_id: int) -> Site:
    site = session.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site introuvable")
    return site


@router.get("/", response_model=List[ManualPageRead])
def list_pages(site_id: int, session: Session = Depends(get_db_session)) -> List[ManualPage]:
    _get_site(session, site_id)
    return session.exec(select(ManualPage).where(ManualPage.site_id == site_id)).all()


@router.post("/", response_model=ManualPageRead, status_code=status.HTTP_201_CREATED)
def create_page(
    site_id: int,
    payload: ManualPageCreate,
    session: Session = Depends(get_db_session),
) -> ManualPage:
    _get_site(session, site_id)
    page = ManualPage(site_id=site_id, **payload.dict())
    session.add(page)
    session.commit()
    session.refresh(page)
    return page


@router.get("/{page_id}", response_model=ManualPageRead)
def get_page(site_id: int, page_id: int, session: Session = Depends(get_db_session)) -> ManualPage:
    page = session.get(ManualPage, page_id)
    if not page or page.site_id != site_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page introuvable")
    return page


@router.put("/{page_id}", response_model=ManualPageRead)
def update_page(
    site_id: int,
    page_id: int,
    payload: ManualPageUpdate,
    session: Session = Depends(get_db_session),
) -> ManualPage:
    page = session.get(ManualPage, page_id)
    if not page or page.site_id != site_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page introuvable")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(page, key, value)
    page.updated_at = datetime.utcnow()
    session.add(page)
    session.commit()
    session.refresh(page)
    return page


@router.delete("/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_page(site_id: int, page_id: int, session: Session = Depends(get_db_session)) -> None:
    page = session.get(ManualPage, page_id)
    if not page or page.site_id != site_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page introuvable")
    session.delete(page)
    session.commit()
