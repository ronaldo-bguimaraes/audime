"""ARQ WorkerSettings for the Audime extraction worker.

Usage::

    arq app.workers.arq_settings.WorkerSettings

Or via docker-compose::

    command: arq app.workers.arq_settings.WorkerSettings
"""

from arq import create_pool
from arq.connections import RedisSettings

from app.core.config import settings
from app.services.storage_service import get_s3_client


async def startup(ctx: dict) -> None:
    """Initialise shared resources for the worker."""
    from abstract.engine import SessionLocal

    ctx["db_session_factory"] = SessionLocal

    # R2 / S3 client (sync boto3 — call via asyncio.to_thread in tasks)
    ctx["r2_client"] = get_s3_client()
    ctx["bucket"] = settings.r2_storage_bucket


async def shutdown(ctx: dict) -> None:
    """Clean up shared resources."""
    db_factory = ctx.pop("db_session_factory", None)
    if db_factory is not None:
        db_factory.close_all()


class WorkerSettings:
    """ARQ worker configuration — discovered by the ``arq`` CLI."""

    functions = ["app.workers.tasks.executar_extracao"]

    on_startup = startup
    on_shutdown = shutdown

    redis_settings = RedisSettings(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        database=settings.redis_db,
    )

    # Allow up to 5 concurrent jobs per worker
    max_jobs = 5

    # Timeout per job: 10 minutes (download + parse + upload)
    job_timeout = 600

    # Keep job results for 2 hours so clients can poll the status
    keep_result = 7200

    # Retry up to 3 times on failure
    max_tries = 3

    # Check in with Redis every 60 seconds so the health-check key stays alive
    health_check_interval = 60

    # Custom queue name for Audime extractions
    queue_name = "audime:extracoes"
