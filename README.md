# Générateur d'annuaires métiers

Cette plateforme propose un backend FastAPI et un frontend React permettant de créer des annuaires métiers alimentés par l'API SIRENE. Elle inclut :

- un back-office pour configurer les filtres SIRENE, les prompts OpenAI et les pages manuelles ;
- un importeur respectant la pagination par curseur de l'API SIRENE (V3), avec prise en compte des établissements fermés ;
- une génération de contenu via OpenAI configurable par template ;
- un géocodage des adresses via la Base Adresse Nationale pour l'affichage sur carte.

## Démarrage rapide

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
# Démarrage assisté sans fichier `.env`
python -m app.cli --sirene-api-key "votre_cle_api" --reload

# Démarrage classique (en supposant les variables déjà définies)
# uvicorn app.main:app --reload
```

Le lanceur `python -m app.cli` permet de fournir les paramètres sensibles directement via la ligne de commande ou via des invites interactives. Les valeurs sont appliquées à l'environnement d'exécution avant de démarrer Uvicorn. Cela évite de créer un fichier `.env` si vous ne le souhaitez pas.

Vous pouvez toujours définir les variables d'environnement dans un fichier `.env` à la racine du backend si vous préférez :

```env
GENERATEUR_DATABASE_URL=sqlite:///./data/app.db
GENERATEUR_SIRENE_API_KEY=votre_cle_api
GENERATEUR_OPENAI_API_KEY=votre_cle_openai
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Par défaut, le proxy Vite redirige les appels `/api` vers `http://localhost:8000`.

## Fonctionnalités clés

- **Gestion des sites** : création de sites d'annuaires avec filtres SIRENE personnalisés.
- **Pages manuelles** : éditeur simple permettant d'ajouter des contenus enrichis.
- **Imports SIRENE** : création de tâches d'import respectant les limites (30 requêtes/minute, 1000 résultats/page) et suivi des fermetures.
- **Génération OpenAI** : prompts configurables par site avec test de rendu.
- **Géocodage BAN** : géocodage différé des adresses et visualisation Leaflet des établissements.

## Tests

Des tests peuvent être ajoutés via `pytest` côté backend et les outils React Testing Library côté frontend.
