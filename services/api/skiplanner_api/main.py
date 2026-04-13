from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import flights, recommendations, resorts


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-seed in development
    from .db_seed import seed
    await seed()
    yield


app = FastAPI(
    title="skiMate API",
    version="0.1.0",
    description="skiMate MVP: resorts, map GeoJSON, flight search (Amadeus optional).",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resorts.router)
app.include_router(flights.router)
app.include_router(recommendations.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.api_env}
