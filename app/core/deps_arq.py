"""FastAPI dependency for ARQ Redis pool.

The pool itself is created in the FastAPI lifespan (see app/main.py)
and stored in app.state.arq_pool. This module provides the getter.
"""

from fastapi import HTTPException, Request, status
from arq.connections import ArqRedis


async def get_arq_pool(request: Request) -> ArqRedis:
    """Return the shared ArqRedis pool from app.state.

    Raises HTTP 503 if the pool is unavailable (Redis not connected).
    """
    pool: ArqRedis | None = request.app.state.arq_pool
    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Fila de tarefas indisponível (Redis desconectado)",
        )
    return pool
