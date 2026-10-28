# ARQ Part 2: Audime Implementation

## Audime Usage: The Synchronous NFC-e Extraction Bottleneck

The endpoint `POST /v1/extracoes` (in `app/api/v1/endpoints/extracoes.py`) currently **synchronously** executes the `executar_extracao()` function in `app/services/extracao_service.py`. The current flow:

```
POST /v1/extracoes → download_url() → upload_to_r2() → parse_nfce() → INSERTs in DB → response
```

This blocks the Uvicorn worker for the entire process (download + parse + writes). If the URL is slow, if SEFAZ takes time, if parsing fails — the client waits. Worse: if the worker restarts, the extraction is lost.

### Where ARQ Would Fit

1. **Endpoint becomes producer**: `POST /v1/extracoes` enqueues an ARQ job and returns `{ "job_id": "...", "status": "queued" }` immediately (HTTP 202 Accepted)
2. **ARQ worker processes in background**: performs download, upload, parse, and persistence
3. **Client polls the result**: `GET /v1/extracoes/{id_extracao}/status` queries status in DB + Redis
4. **Resilience**: if the worker crashes during processing, the job is automatically requeued (pessimistic execution)

### Impact on Docker Compose

```yaml
redis:
  image: redis:7-alpine
  container_name: audime-redis
  restart: unless-stopped
  ports:
    - "${REDIS_PORT:-6379}:6379"
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 5s

worker:
  build: .
  container_name: audime-worker
  restart: unless-stopped
  command: arq app.workers.arq_settings.WorkerSettings
  environment:
    REDIS_HOST: redis
    DB_POSTGRES_HOST: postgres
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_started
```

### Impact on Dependencies

```toml
dependencies = [
    "arq>=0.28.0",
    "redis[hiredis]>=4.2.0,<6",
]
```

### Impact on Configuration

```python
class Settings(BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str | None = None
    redis_db: int = 1
```

### How the Endpoint Would Change (Conceptual)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from arq.connections import ArqRedis

router = APIRouter(prefix="/v1/extracoes", tags=["extracoes"])

@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def criar_extracao(
    body: ExtracaoRequest,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_current_user_id),
    arq: ArqRedis = Depends(get_arq_pool),
):
    extracao = Extracao(id_usuario=id_usuario, status=ExtracaoStatus.PENDING)
    db.add(extracao)
    db.commit()
    job = await arq.enqueue_job(
        "executar_extracao",
        url=body.url,
        id_extracao=extracao.id_extracao,
        id_usuario=id_usuario,
        _job_id=f"extracao:{extracao.id_extracao}",
        _defer_by=0,
    )
    return {
        "job_id": job.job_id,
        "id_extracao": extracao.id_extracao,
        "status": "queued",
    }

@router.get("/{id_extracao}/status")
async def obter_status_extracao(
    id_extracao: int,
    db: Session = Depends(get_db),
):
    extracao = db.get(Extracao, id_extracao)
    if not extracao:
        raise HTTPException(status_code=404)
    return {"id_extracao": id_extracao, "status": extracao.status.value}
```

### How the ARQ Task Would Work (Conceptual)

```python
from httpx import AsyncClient
from app.services.parser_nfce import parse_nfce
from app.services.storage_service import generate_filename, hash_sha256

OUTPUT_PREFIX = "imports/html"

async def executar_extracao(ctx: dict, url: str, id_extracao: int, id_usuario: int):
    db_session_factory = ctx["db_session_factory"]
    r2_client = ctx["r2_client"]

    with db_session_factory() as db:
        from abstract.models.core import Extracao, ExtracaoStatus
        from abstract.models.raw import Importacao, ItemNota, Nota
        import posixpath

        try:
            extracao = db.get(Extracao, id_extracao)
            extracao.status = ExtracaoStatus.RUNNING
            db.commit()

            async with AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                html_bytes = response.content

            sha256 = hash_sha256(html_bytes)
            filename = generate_filename()
            key = posixpath.join(OUTPUT_PREFIX, filename)

            r2_client.put_object(
                Body=html_bytes,
                Bucket=ctx["bucket"],
                Key=key,
                Metadata={"sha256": sha256},
            )

            extracao.status = ExtracaoStatus.DONE
            db.commit()

        except Exception:
            extracao.status = ExtracaoStatus.ERROR
            db.commit()
            raise
```
