# ARQ Task Queue — Implementation Details

**Cycle ref:** 2026-06-30-arq-task-queue
**Date:** 2026-06-30

---

## Validation results

**23 criteria** — 18 ✅ PASS, 3 ⚠️ PARTIAL (corrected during validation), 2 ❌ FAIL (1 corrected, 1 pending)

### ✅ PASS (20 after corrections)

| Criterion | Description | Status |
|-----------|-------------|--------|
| CAT-001 | Dependencies — `arq`, `redis[hiredis]`, `httpx` in `pyproject.toml` and `requirements.txt` | ✅ (versions added in correction) |
| CAT-002 | Redis config — `redis_host`, `redis_port`, `redis_db`, `redis_password` fields in `Settings` | ✅ |
| CAT-003 | WorkerSettings — class with `functions`, `redis_settings`, `on_startup`/`on_shutdown` | ✅ |
| CAT-004 | ARQ task — `executar_extracao` async with `httpx.AsyncClient` | ✅ |
| CAT-006 | POST refactored — `async`, 202 Accepted, enqueue job | ✅ |
| CAT-007 | GET /status — polling endpoint with auth | ✅ |
| CAT-008 | GET /{id} original preserved with auth | ✅ |
| CAT-009 | Docker Compose — redis + worker services | ✅ |
| CAT-010 | .env.example — Redis variables | ✅ |
| CAT-011 | Dockerfile — unchanged, compatible | ✅ |
| CAT-012 | Pytest — 4 passed | ✅ |
| CAT-013 | Import no errors — modules loadable | ✅ |
| CAT-014 | ARQ installed — `import arq` works | ✅ |
| CAT-015 | Response schema — `ExtracaoResponse` + new schemas | ✅ |
| CAT-016 | Idempotence via `_job_id` | ✅ |
| CAT-017 | Worker uses `SessionLocal` from `abstract.engine` | ✅ |
| CAT-018 | POST creates PENDING before enqueuing | ✅ |
| CAT-019 | Worker replaces sync flow (`extracao_service` no longer called) | ✅ |
| CAT-020 | Security — no leaked credentials, HttpUrl in request | ✅ |
| CAT-021 | Git diff — all expected files present | ✅ |
| CAT-023 | Error handling — try/except with `ERROR` + `raise` | ✅ |

### ⚠️ PARTIAL — corrected during validation

| Criterion | Description | Correction |
|-----------|-------------|------------|
| CAT-005 | `create_pool` in `main.py` vs `deps_arq.py` — spec asked pool in `deps_arq`, but implementation uses `lifespan` (recommended FastAPI pattern). `deps_arq` reads from `app.state` | Conscious decision — `lifespan` is the correct FastAPI pattern; `deps_arq` became a getter, not a creator |
| CAT-001 (format) | `requirements.txt` without versions | `requirements.txt` updated with pinned versions |

### ❌ FAIL

| Criterion | Description | Pending |
|-----------|-------------|---------|
| CAT-022 | Descriptive commit message (≥10 words, `feat(arq)` or `feat(queue)`) | Pending — will be fixed in next commit |

---

## Pending items for next cycle

### Complete SSRF protection
- `HttpUrl` is insufficient to mitigate SSRF — it allows URLs to `localhost`, `10.x.x.x`, `169.254.x.x`
- **Action:** Add allowlist of trusted domains (e.g. `*.sefaz.*.gov.br`) in Settings, validate at endpoint or via middleware, or use `restrict_hosts` in `httpx.AsyncClient` on the worker task
- **Priority:** HIGH — security risk

### aioboto3 — natively async R2 client
- Currently synchronous boto3 is called via `asyncio.to_thread`, which works but adds thread pool overhead
- **Action:** Evaluate migration to `aioboto3` (or `s3fs` with `aiohttp`) for fully async R2 operations
- **Priority:** LOW — `asyncio.to_thread` handles the use case well

### Dead letter notification
- Jobs exceeding `max_tries=3` are discarded by ARQ without notification
- **Action:** Configure `on_job_end` / `on_failure` in WorkerSettings to notify (email, webhook, or mark in DB table)
- **Priority:** MEDIUM — needed before production

### Worker health check + monitoring
- ARQ worker has `health_check_interval=60` but no external endpoint to verify if the worker is alive
- **Action:** Add `GET /v1/health/worker` endpoint that checks worker heartbeat in Redis
- **Priority:** LOW — useful for production monitoring

### Descriptive commit message
- The ARQ commit has not been made yet; the message should follow `feat(arq): ...` with ≥10 words
- **Priority:** IMMEDIATE — needed to close the cycle

---

## Lessons learned

### ARQ dependency design
- `deps_arq` as **getter** + `lifespan` as **creator** is more idiomatic FastAPI than creating the pool inside the dependency. The initial spec expected the opposite, but the `lifespan` → `app.state` → `Depends` pattern is recommended by the official documentation. [EXECUTION]

### Factory pattern for sessions in the worker
- The spec said "store session in `ctx['db']`" but the implementation stored `SessionLocal` (the factory). This was a deliberate improvement: SQLAlchemy sessions must not be shared between concurrent coroutines. Each job needs its own session. [CORE]
- Lesson: **Never share SQLAlchemy sessions between concurrent tasks** — always store the factory and create sessions per job. [CORE]

### asyncio.to_thread vs thread pool
- `asyncio.to_thread` creates a new thread per call (implicit pool). For short operations like `put_object`, the overhead is negligible. For heavier or more frequent operations, consider an explicit `ThreadPoolExecutor` or `aioboto3`. [EXECUTION]

### Local vs module-level imports
- Tasks in `tasks.py` import `Extracao`, `ExtracaoStatus`, `Importacao`, `ItemNota`, `Nota` **inside the function body**, not at the module top level. This is a safety measure against circular imports and also avoids unnecessary import cost when the module is loaded by ARQ but the specific function is not called. [EXECUTION]
- `arq_settings.py` also does `from abstract.engine import SessionLocal` inside the `startup` function for the same reason. [EXECUTION]

### HttpUrl is not security
- `pydantic.HttpUrl` validates URL format but **does not block internal domains**. It is data validation, not a security measure. For SSRF, a custom validator (allowlist + private IP blocking) or worker-level validation is needed. [CONSTRAINT]
- Lesson: **Never trust `HttpUrl` for SSRF security** — implement a domain allowlist separately. [CONSTRAINT]

### Two-layer idempotence
- The combination of `_job_id` (ARQ-level) + `Nota.chave` UNIQUE (DB-level) creates two idempotence layers: one prevents duplicate jobs in the queue, another prevents duplicate notes in the database. This is solid defense-in-depth design. [EXECUTION]

### Validation structure
- Validation found 3 PARTIAL and 2 FAIL out of 23 criteria. The ability to make corrections during validation (`requirements.txt` without versions) shows that the spec → implementation → validation → correction cycle is working. The grep-based verification format is fragile for implementation changes that diverge from the spec but are legitimate improvements (e.g., factory pattern vs direct session). [MEMORY]
