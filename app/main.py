import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI
from app.api.v1.endpoints import analytics, auth, dashboard, extracoes, faturas, notas
from app.core.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator:
    """FastAPI lifespan — manages the shared ARQ Redis pool."""
    if settings.app_env == "production" and not settings.jwt_secret:
        raise RuntimeError(
            "JWT_SECRET must be set in production. "
            "Generate a long random string (min 32 chars) and set it in .env"
        )
    pool = None
    try:
        pool = await create_pool(
            RedisSettings(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                database=settings.redis_db,
            ),
            retry=1,  # only 1 retry on startup
        )
    except Exception as exc:
        logger.warning("Redis not available — ARQ queue disabled: %s", exc)
    _app.state.arq_pool = pool
    yield
    if pool is not None:
        await pool.close()


app = FastAPI(
    title="Audime API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(extracoes.router)
app.include_router(notas.router)
app.include_router(faturas.router)
app.include_router(dashboard.router)
app.include_router(analytics.router)


@app.get("/v1/health")
def health():
    return {"status": "ok"}
