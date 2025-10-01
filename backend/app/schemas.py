from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class SiteCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    sirene_filters: dict[str, str] | None = None
    openai_prompt: Optional[str] = None


class SiteRead(SiteCreate):
    id: int
    created_at: datetime


class ManualPageCreate(BaseModel):
    title: str
    slug: str
    content: str
    seo_description: Optional[str] = None


class ManualPageUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    seo_description: Optional[str] = None


class ManualPageRead(ManualPageCreate):
    id: int
    site_id: int
    created_at: datetime
    updated_at: datetime


class EstablishmentRead(BaseModel):
    id: int
    site_id: int
    siren: str
    nic: str
    siret: str
    business_name: Optional[str]
    naf_code: Optional[str]
    naf_label: Optional[str]
    address: Optional[str]
    postal_code: Optional[str]
    city: Optional[str]
    department: Optional[str]
    is_active: bool
    closure_label: Optional[str]
    imported_at: datetime
    last_seen_at: datetime
    geo_lat: Optional[float]
    geo_lon: Optional[float]
    geo_status: Optional[str]
    extra_metadata: Optional[dict[str, Any]]


class ImportJobCreate(BaseModel):
    naf_code: Optional[str] = None
    department: Optional[str] = None
    city: Optional[str] = None


class ImportJobRead(ImportJobCreate):
    id: int
    site_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    cursor: Optional[str]
    total_imported: int
    total_closed: int
    total_errors: int
    last_error: Optional[str]


class PromptTemplateCreate(BaseModel):
    label: str
    prompt: str
    scope: str = "city"


class PromptTemplateRead(PromptTemplateCreate):
    id: int
    site_id: int
    created_at: datetime


class ContentGenerationRequest(BaseModel):
    template_id: int
    variables: dict[str, str]


class ContentGenerationResponse(BaseModel):
    prompt: str
    content: str
