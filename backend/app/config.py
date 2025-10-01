from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(
        default="sqlite:///./data/app.db",
        description="URL de connexion à la base de données",
    )
    sirene_base_url: str = Field(
        default="https://api.insee.fr/entreprises/sirene/V3",
        description="Endpoint racine de l'API SIRENE",
    )
    sirene_api_key: str | None = Field(
        default=None, description="Clé API SIRENE ou token OAuth"
    )
    sirene_oauth_client_id: str | None = None
    sirene_oauth_client_secret: str | None = None
    sirene_rate_limit_per_minute: int = 30
    sirene_default_page_size: int = 1000
    openai_api_key: str | None = None
    ban_base_url: str = "https://api-adresse.data.gouv.fr"

    class Config:
        env_file = ".env"
        env_prefix = "GENERATEUR_"


def get_settings() -> Settings:
    return Settings()
