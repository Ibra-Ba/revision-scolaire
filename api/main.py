
from fastapi import FastAPI

from api.routers.curriculum import router as curriculum_router

app = FastAPI(
    title="Révi’Pote",
    description="L'API de ton compagnon de révision scolaire.",
    version="0.1.0",
)

app.include_router(curriculum_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
