from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..dependencies import get_db_session
from ..models import PromptTemplate, Site
from ..schemas import PromptTemplateCreate, PromptTemplateRead

router = APIRouter(prefix="/sites/{site_id}/prompts", tags=["prompts"])


def _get_site(session: Session, site_id: int) -> Site:
    site = session.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site introuvable")
    return site


@router.get("/", response_model=List[PromptTemplateRead])
def list_prompts(site_id: int, session: Session = Depends(get_db_session)) -> List[PromptTemplate]:
    _get_site(session, site_id)
    return session.exec(select(PromptTemplate).where(PromptTemplate.site_id == site_id)).all()


@router.post("/", response_model=PromptTemplateRead, status_code=status.HTTP_201_CREATED)
def create_prompt(
    site_id: int,
    payload: PromptTemplateCreate,
    session: Session = Depends(get_db_session),
) -> PromptTemplate:
    _get_site(session, site_id)
    prompt = PromptTemplate(site_id=site_id, **payload.dict())
    session.add(prompt)
    session.commit()
    session.refresh(prompt)
    return prompt


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt(site_id: int, prompt_id: int, session: Session = Depends(get_db_session)) -> None:
    prompt = session.get(PromptTemplate, prompt_id)
    if not prompt or prompt.site_id != site_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt introuvable")
    session.delete(prompt)
    session.commit()
