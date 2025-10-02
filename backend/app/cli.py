"""Command-line utilities for running the FastAPI application without relying on a .env file."""

from __future__ import annotations

import argparse
import os
from getpass import getpass

import uvicorn

from .config import Settings


def _set_env_if_provided(name: str, value: str | None) -> None:
    if value:
        os.environ[name] = value


def _request_missing_secret(value: str | None, prompt: str, allow_empty: bool = False) -> str | None:
    if value is not None:
        return value
    entered = getpass(prompt)
    if not entered and not allow_empty:
        return None
    return entered or None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Démarre l'API Générateur d'annuaires métiers en configurant les paramètres nécessaires."
    )
    parser.add_argument(
        "--database-url",
        dest="database_url",
        help="URL de connexion à la base de données (ex: sqlite:///./data/app.db)",
    )
    parser.add_argument(
        "--sirene-api-key",
        dest="sirene_api_key",
        help="Clé API SIRENE. Si omise, elle sera demandée lors de l'exécution.",
    )
    parser.add_argument(
        "--sirene-oauth-client-id",
        dest="sirene_oauth_client_id",
        help="Identifiant client OAuth SIRENE (si vous utilisez l'authentification OAuth).",
    )
    parser.add_argument(
        "--sirene-oauth-client-secret",
        dest="sirene_oauth_client_secret",
        help="Secret client OAuth SIRENE (si vous utilisez l'authentification OAuth).",
    )
    parser.add_argument(
        "--openai-api-key",
        dest="openai_api_key",
        help="Clé API OpenAI pour la génération de contenus (facultatif).",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Hôte à utiliser pour le serveur Uvicorn (par défaut 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port à utiliser pour le serveur Uvicorn (par défaut 8000).",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Active le rechargement automatique du serveur (utile en développement).",
    )
    return parser


def apply_runtime_settings(arguments: argparse.Namespace) -> None:
    settings = Settings()  # charge les valeurs existantes (env, .env, valeurs par défaut)
    database_url = arguments.database_url or settings.database_url
    sirene_api_key = arguments.sirene_api_key or settings.sirene_api_key
    sirene_oauth_client_id = arguments.sirene_oauth_client_id or settings.sirene_oauth_client_id
    sirene_oauth_client_secret = arguments.sirene_oauth_client_secret or settings.sirene_oauth_client_secret
    openai_api_key = arguments.openai_api_key or settings.openai_api_key

    if not sirene_api_key:
        sirene_api_key = _request_missing_secret(
            sirene_api_key,
            "Clé API SIRENE (obligatoire, laisser vide pour annuler): ",
        )
        if not sirene_api_key:
            raise RuntimeError("Aucune clé API SIRENE fournie. Impossible de démarrer l'application.")

    if not sirene_oauth_client_secret and arguments.sirene_oauth_client_secret is None:
        sirene_oauth_client_secret = _request_missing_secret(
            sirene_oauth_client_secret,
            "Secret client OAuth SIRENE (laisser vide si non utilisé): ",
            allow_empty=True,
        )

    if not openai_api_key and arguments.openai_api_key is None:
        openai_api_key = _request_missing_secret(
            openai_api_key,
            "Clé API OpenAI (laisser vide si non utilisée): ",
            allow_empty=True,
        )

    _set_env_if_provided("GENERATEUR_DATABASE_URL", database_url)
    _set_env_if_provided("GENERATEUR_SIRENE_API_KEY", sirene_api_key)
    _set_env_if_provided("GENERATEUR_SIRENE_OAUTH_CLIENT_ID", sirene_oauth_client_id)
    _set_env_if_provided("GENERATEUR_SIRENE_OAUTH_CLIENT_SECRET", sirene_oauth_client_secret)
    _set_env_if_provided("GENERATEUR_OPENAI_API_KEY", openai_api_key)


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    apply_runtime_settings(args)

    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":  # pragma: no cover - point d'entrée CLI
    main()
