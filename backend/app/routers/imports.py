import asyncio
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlmodel import Session, select

from ..database import get_session
from ..dependencies import get_db_session
from ..models import ImportJob, Site
from ..schemas import ImportJobCreate, ImportJobRead
from ..services.geocoding import geocode_in_background
from ..services.sirene import SireneImporter

router = APIRouter(prefix="/sites/{site_id}/imports", tags=["imports"])


def _get_site(session: Session, site_id: int) -> Site:
    site = session.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site introuvable")
    return site


@router.get("/", response_model=List[ImportJobRead])
def list_import_jobs(site_id: int, session: Session = Depends(get_db_session)) -> List[ImportJob]:
    _get_site(session, site_id)
    return session.exec(select(ImportJob).where(ImportJob.site_id == site_id)).all()


@router.post("/", response_model=ImportJobRead, status_code=status.HTTP_201_CREATED)
def create_import_job(
    site_id: int,
    payload: ImportJobCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_db_session),
) -> ImportJob:
    _get_site(session, site_id)
    job = ImportJob(site_id=site_id, **payload.dict())
    session.add(job)
    session.commit()
    session.refresh(job)
    background_tasks.add_task(schedule_import_job, job.id)
    return job


def schedule_import_job(job_id: int) -> None:
    loop = asyncio.get_event_loop()
    loop.create_task(run_import_job(job_id))


async def run_import_job(job_id: int) -> None:
    importer = SireneImporter()
    with get_session() as session:
        job = session.get(ImportJob, job_id)
        if not job:
            return
        await importer.import_for_site(session, job)
        await geocode_in_background(get_session, job.site_id)
