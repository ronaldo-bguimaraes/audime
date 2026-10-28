# Cycle: ARQ Task Queue

**Date:** 2026-06-30
**Agent:** especulador (validation mode)
**Effort:** Refactoring the NFC-e extraction flow from synchronous to asynchronous

---

## What was implemented

### New
- `app/workers/arq_settings.py` — `WorkerSettings` with `functions`, `redis_settings`, `on_startup`/`on_shutdown`, `max_jobs=5`, `job_timeout=600`, `keep_result=7200`, `max_tries=3`, `queue_name="audime:extracoes"`
- `app/workers/tasks.py` — task `async def executar_extracao(ctx, *, url, id_extracao, id_usuario)` with: download via `httpx.AsyncClient`, hash + upload to R2 via `asyncio.to_thread`, persist `Importacao` / `Nota` / `ItemNota`, try/except with `ERROR`/`DONE`
- `app/workers/__init__.py` — empty package
- `app/core/deps_arq.py` — dependency `get_arq_pool` that reads `request.app.state.arq_pool` and raises HTTP 503 if `None`

### Modified
- `app/core/config.py` — added `redis_host`, `redis_port`, `redis_db`, `redis_password`
- `app/main.py` — lifespan with `create_pool` tolerant to missing Redis (`logger.warning` + pool = `None`)
- `app/api/v1/endpoints/extracoes.py` — POST async (202 Accepted, enqueue with `_job_id`), GET `/status`, GET `/{id}` (both with auth)
- `app/api/v1/schemas.py` — `ExtracaoJobResponse`, `ExtracaoStatusResponse`, `HttpUrl` in request
- `pyproject.toml` — added `arq>=0.28.0`, `redis[hiredis]>=4.2.0,<6`, `httpx>=0.28.0`
- `requirements.txt` — same deps with pinned versions
- `docker-compose.yml` — `redis` (7-alpine) and `worker` (arq CLI) services
- `.env.example` — `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_PASSWORD` variables

---

## Technical decisions

### Lifespan pattern (main.py)
The ARQ Redis pool is created in the FastAPI `lifespan` and stored in `app.state.arq_pool`. If Redis is unavailable at startup, a warning is logged and `pool = None` — the system continues without a queue. `deps_arq.get_arq_pool` reads from `app.state` and returns HTTP 503 if the pool is `None`.

**Rationale:** `lifespan` is the official FastAPI mechanism for resources requiring setup/teardown. It avoids lazy initialization and guarantees the pool is closed on shutdown.

### Session factory in worker ctx (arq_settings.py)
Unlike the original spec (which suggested storing a session in `ctx['db']`), the implementation stores the **factory** `SessionLocal` in `ctx['db_session_factory']`. Each task creates its own session via `db_factory()`.

**Rationale:** SQLAlchemy sessions are **not thread-safe** nor coroutine-safe. Since ARQ can execute multiple jobs concurrently (`max_jobs=5`), each job needs its own session. The factory pattern is the correct approach.

### asyncio.to_thread for synchronous boto3
Upload to R2 via `r2_client.put_object()` (synchronous boto3) is executed with `await asyncio.to_thread(...)`.

**Rationale:** Although the ARQ worker is a separate process, it runs in an asyncio event loop. Synchronous calls block the loop and prevent other concurrent jobs from progressing. `asyncio.to_thread` delegates the call to a thread pool, freeing the event loop.

**Tradeoff:** A cleaner alternative would be `aioboto3`, but it adds another dependency. `asyncio.to_thread` is standard library (Python 3.9+) and sufficient for MVP.

### HttpUrl for SSRF mitigation (schemas.py)
The `url` field in `ExtracaoRequest` uses `pydantic.HttpUrl` instead of `str`.

**Rationale:** `HttpUrl` validates that the string is a well-formed URL with http/https scheme, as a first layer of defense against SSRF. A domain allowlist is still needed (pending).

**Limitation:** `HttpUrl` does not block internal domains (`localhost`, `10.x.x.x`, `169.254.x.x`). Full SSRF validation requires allowlist + private address blocking, which goes to the next cycle.

### Authentication on GET endpoints
Both `GET /v1/extracoes/{id}/status` and `GET /v1/extracoes/{id}` require JWT via `Depends(get_current_user_id)` and verify `extracao.id_usuario != id_usuario`.

**Rationale:** Per-user data isolation — one user cannot poll the status of another user's extractions. Consistent with the project's other endpoints.

### _job_id for idempotence
The job is enqueued with `_job_id=f"extracao:{id_extracao}"`.

**Rationale:** If the same `_job_id` already exists in Redis (pending or processing job), ARQ rejects the new enqueue, guaranteeing no duplicate jobs for the same extraction. The NFC key uniqueness (`Nota.chave` has `unique=True`) is the second layer of idempotence.

### Graceful degradation — Redis unavailable
If Redis is not available at startup, the application continues functioning:
- `app.state.arq_pool = None`
- The POST endpoint returns HTTP 503 ("Task queue unavailable")
- The GET endpoints continue working (they only query the DB)

---

## Files created/modified

| File | Type | Description |
|------|------|-------------|
| `app/workers/arq_settings.py` | NEW | WorkerSettings with startup/shutdown, redis_settings, job config |
| `app/workers/tasks.py` | NEW | Main task `executar_extracao` (download, upload, parse, persist) |
| `app/workers/__init__.py` | NEW | Empty package |
| `app/core/deps_arq.py` | NEW | FastAPI dependency for ARQ pool |
| `app/core/config.py` | MODIFIED | +redis_host, redis_port, redis_db, redis_password |
| `app/main.py` | MODIFIED | Lifespan with tolerant create_pool |
| `app/api/v1/endpoints/extracoes.py` | MODIFIED | POST async + GET /status + auth |
| `app/api/v1/schemas.py` | MODIFIED | +ExtracaoJobResponse, ExtracaoStatusResponse, HttpUrl |
| `pyproject.toml` | MODIFIED | +arq, redis[hiredis], httpx |
| `requirements.txt` | MODIFIED | +arq, redis[hiredis], httpx (with versions) |
| `docker-compose.yml` | MODIFIED | +redis service, +worker service |
| `.env.example` | MODIFIED | +REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD |
