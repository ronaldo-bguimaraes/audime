# ARQ Part 2b: Risks, Alternatives, and Conclusion

*Continuation of `arq_part2_implementation.md` — risk analysis and trade-offs.*

---

## Why NOT to Use (Risks and Disadvantages)

1. **Maintenance-only mode**: ARQ will not receive new features. For a new project, this is a strategic risk. Alternative: Taskiq (more modern) or Celery (more established).
2. **Redis as a dependency**: Adds a new service to the stack (more memory, monitoring, backup). Counterpoint: Redis is mature, lightweight (~5MB), and often already in the ecosystem.
3. **Jobs may be called more than once**: Pessimistic execution means every job needs to be **idempotent**. NFC-e extraction is naturally idempotent (key is UNIQUE in the DB), but it is an explicit design requirement.
4. **Pickle serialization**: ARQ uses pickle to serialize jobs by default — unsafe for data from untrusted sources. Mitigation: use a custom serializer (MsgPack) or never enqueue sensitive data.
5. **DB session in the worker**: The ARQ worker runs in a separate process — it cannot share the FastAPI session. It needs its own pool created in `on_startup`. `SessionLocal` already exists in `abstract.engine` and can be reused.
6. **Operational complexity**: You now manage 2 processes (API + Worker) + Redis. The docker-compose grows.
7. **Overhead for simple tasks**: If NFC-e extraction takes <2s, maybe FastAPI BackgroundTasks is sufficient. But the risk of losing jobs on server restart remains.

---

## Pros and Cons

| Pros | Cons |
|------|------|
| Async-first, natural integration with FastAPI | Maintenance-only mode (no new features) |
| Ultra-lean code (~700 lines) — easy to understand | Only supports Redis as broker |
| Pessimistic execution = jobs are not lost in crashes | Requires Redis (extra stack dependency) |
| Automatic retry with backoff (+ `raise Retry()`) | Jobs can run more than once (requires idempotency) |
| Future scheduling + built-in cron jobs | No workflow primitives (group/chord) |
| Shared Redis pool via `ctx` | Pickle as default serializer (unsafe) |
| `arq` CLI for running worker + health check | Relatively small project (smaller community than Celery) |
| Performance ~7-40x better than RQ | Fewer tutorials and examples than Celery |
| Native health check via Redis key | |
| Multiple queues with priority | |

---

## Viable Alternatives for Audime

1. **FastAPI BackgroundTasks** — for short tasks (<5s), no tracking needed. Does not solve the persistence problem.
2. **Celery** — the industry standard, supports multiple brokers, complex workflows. High overhead for Audime's scope (~100k+ lines of Celery code).
3. **Taskiq** — modern async-first alternative, no maintenance mode. Less mature than ARQ, but with more growth potential.
4. **Dramatiq** — thread-based, good for I/O-bound jobs. Not async-first like ARQ.
5. **RQ (Redis Queue)** — synchronous, simple, but blocking with asyncio.

---

## Conclusion

**ARQ is the right choice for Audime today.** The project uses FastAPI (100% async), Redis is simple to add to Docker Compose, and NFC-e extraction is a classic task queue use case: I/O-bound (download + parse + upload), with a need for resilience (retry on network failure), and where the client does not need to wait for the synchronous response.

The migration is low risk because:
- The extraction code (`executar_extracao`) exists and works — it just needs to be adapted to run in the worker
- The `Extracao` model already has `status` (PENDING → RUNNING → DONE/ERROR) — exactly what ARQ needs
- The NFC-e key (UNIQUE) guarantees natural idempotency
- The `workers/` directory already exists in the project — just add `workers/arq_tasks.py`

The main point of attention is ARQ's **maintenance-only mode**. For an MVP, this is irrelevant. For a long-term product, it is worth monitoring Taskiq as a future alternative.

> ⚠️ **Important note**: ARQ v0.16 had a **complete rewrite** that broke compatibility with pre-v0.16 code. Any tutorials or examples prior to 2019 may be outdated. Always use the v0.28 documentation.
