from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel


class Site(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    slug: str = Field(index=True, sa_column_kwargs={"unique": True})
    description: Optional[str] = None
    sirene_filters: dict[str, str] | None = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    openai_prompt: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    pages: list["ManualPage"] = Relationship(back_populates="site")
    establishments: list["Establishment"] = Relationship(back_populates="site")


class ManualPage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    site_id: int = Field(foreign_key="site.id")
    title: str
    slug: str = Field(index=True)
    content: str
    seo_description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    site: "Site" = Relationship(back_populates="pages")


class Establishment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    site_id: int = Field(foreign_key="site.id", index=True)
    siren: str = Field(index=True)
    nic: str = Field(index=True)
    siret: str = Field(index=True, sa_column_kwargs={"unique": True})
    business_name: Optional[str] = None
    naf_code: Optional[str] = Field(default=None, index=True)
    naf_label: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = Field(default=None, index=True)
    city: Optional[str] = Field(default=None, index=True)
    department: Optional[str] = Field(default=None, index=True)
    is_active: bool = Field(default=True, index=True)
    closure_label: Optional[str] = None
    imported_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)
    geo_lat: Optional[float] = Field(default=None, index=True)
    geo_lon: Optional[float] = Field(default=None, index=True)
    geo_status: Optional[str] = Field(default=None)
    extra_metadata: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )

    site: "Site" = Relationship(back_populates="establishments")


class ImportJob(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    site_id: int = Field(foreign_key="site.id")
    naf_code: Optional[str] = None
    department: Optional[str] = None
    city: Optional[str] = None
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    cursor: Optional[str] = None
    total_imported: int = 0
    total_closed: int = 0
    total_errors: int = 0
    last_error: Optional[str] = None


class PromptTemplate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    site_id: int = Field(foreign_key="site.id")
    label: str
    prompt: str
    scope: str = Field(default="city", description="city|postal_code|custom")
    created_at: datetime = Field(default_factory=datetime.utcnow)
