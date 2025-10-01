from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..dependencies import get_db_session
from ..models import PromptTemplate, Site
from ..schemas import ContentGenerationRequest, ContentGenerationResponse
from ..services.generation import ContentGenerationService

router = APIRouter(prefix="/sites/{site_id}/generate", tags=["generation"])


def _get_site(session: Session, site_id: int) -> Site:
    site = session.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site introuvable")
    return site


@router.post("/", response_model=ContentGenerationResponse)
async def generate_content(
    site_id: int,
    payload: ContentGenerationRequest,
    session: Session = Depends(get_db_session),
) -> ContentGenerationResponse:
    _get_site(session, site_id)
    template = session.get(PromptTemplate, payload.template_id)
    if not template or template.site_id != site_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template introuvable")
    try:
        service = ContentGenerationService()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    content = await service.generate_content(payload.template_id, payload.variables, session)
    prompt = template.prompt.format(**payload.variables)
    return ContentGenerationResponse(prompt=prompt, content=content)
