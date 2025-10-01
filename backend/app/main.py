from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import establishments, generation, imports, pages, prompts, sites

init_db()

app = FastAPI(title="Générateur d'annuaires métiers")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sites.router)
app.include_router(pages.router)
app.include_router(imports.router)
app.include_router(establishments.router)
app.include_router(prompts.router)
app.include_router(generation.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "API de génération d'annuaires métiers opérationnelle"}
