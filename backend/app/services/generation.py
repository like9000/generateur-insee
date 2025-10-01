from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI
from sqlmodel import Session

from ..config import Settings, get_settings
from ..models import PromptTemplate


class ContentGenerationService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        if not self.settings.openai_api_key:
            raise RuntimeError("Clé OpenAI manquante")
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)

    async def generate_content(self, template_id: int, variables: dict[str, Any], session: Session) -> str:
        template = session.get(PromptTemplate, template_id)
        if not template:
            raise ValueError("Template introuvable")
        prompt = template.prompt.format(**variables)
        response = await self.client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )
        return response.output_text  # type: ignore[return-value]
