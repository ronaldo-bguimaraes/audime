---
date: 2026-06-30
topic: ARQ — Async Redis Queue for Task Queue Management
tags: [arq, task-queue, async, redis, background-jobs, fastapi]
sources:
  - title: "ARQ Documentation (v0.28.0)"
    url: "https://arq-docs.helpmanual.io/"
  - title: "ARQ GitHub Repository (python-arq/arq)"
    url: "https://github.com/python-arq/arq"
  - title: "Managing Background Tasks in FastAPI: BackgroundTasks vs ARQ + Redis" — David Muraya
    url: "https://davidmuraya.com/blog/fastapi-background-tasks-arq-vs-built-in"
  - title: "Task Queues — Durable Background Jobs with ARQ and Redis" — StackLesson
    url: "https://www.stacklesson.com/react-fastapi/fastapi-uploads-tasks/ch30-lesson-04-task-queues-with-arq/"
  - title: "Celery Versus ARQ: Choosing the Right Task Queue for Python Applications" — Leapcell
    url: "https://leapcell.io/blog/celery-versus-arq-choosing-the-right-task-queue-for-python-applications"
  - title: "Exploring Python Task Queue Libraries with Load Test" — Steven Yue
    url: "https://stevenyue.com/blogs/exploring-python-task-queue-libraries-with-load-test"
  - title: "Python Task Queue Libraries Compared" — StudyRaid
    url: "https://app.studyraid.com/en/read/15008/518850/celery-vs-other-task-queue-systems"
  - title: FastAPI-ARQ Reference Project — davidmuraya/fastapi-arq
    url: "https://github.com/davidmuraya/fastapi-arq"
---

# ARQ — Async Redis Queue — Overview

## What is ARQ

**ARQ** (Async Redis Queue) is a Python library for asynchronous task queues built on top of Redis and asyncio. Created by Samuel Colvin (also the creator of Pydantic), ARQ was designed as a modern, high-performance successor to RQ.

**Current version:** v0.28.0 (April/2026) — supports Python 3.9 to 3.14.
**Project status:** *Maintenance only mode* ([issue #510](https://github.com/python-arq/arq/issues/510)) — stable and mature, no new features planned, but actively maintained.

### Architecture

ARQ works with three components:

1. **Producer** (your FastAPI app): enqueues jobs by calling `redis.enqueue_job('function_name', args...)`
2. **Redis**: acts as broker and result backend (uses lists, hashes, and sorted sets)
3. **Worker** (separate process): runs `arq app.WorkerSettings`, listens to the queue and processes jobs

### Main Features

| Feature | Description |
|---------|-------------|
| **Fully async** | Built on asyncio — jobs are `async def`, no forking |
| **Pessimistic execution** | Jobs are not removed from the queue until they succeed or definitively fail. If the worker crashes, the job is automatically requeued |
| **Built-in retry** | `raise Retry(defer=N)` for retry with backoff; `max_tries` sets the limit |
| **Scheduling** | `_defer_by` / `_defer_until` for future execution; `cron()` for periodic jobs |
| **Unique Job ID** | Customizable `_job_id` guarantees uniqueness in the queue (Redis transaction) |
| **Results** | `job.result(timeout=N)` to await; `job.status()` for polling |
| **Multiple queues** | Support for `queue_name` to separate priorities |
| **Hooks** | `on_startup`, `on_shutdown`, `on_job_start`, `on_job_end` |
| **Health check** | Worker registers heartbeat in Redis every `health_check_interval` |
| **Serialization** | Pickle by default; customizable (MsgPack, JSON, etc.) |
| **Size** | ~700 lines of code — small, focused, easy to debug |

---

## When to Use ARQ vs Alternatives

| Criteria | ARQ | Celery | Huey | Dramatiq | FastAPI BackgroundTasks |
|----------|-----|--------|------|----------|-------------------------|
| **Async-first** | ✅ native | ⚠️ possible with aio-celery | ❌ synchronous | ✅ threads | ✅ native |
| **Broker** | Redis only | RabbitMQ, Redis, SQS | Redis, SQLite | Redis, RabbitMQ | None (same process) |
| **Persistence** | ✅ Redis | ✅ broker | ✅ Redis | ✅ broker | ❌ volatile |
| **Retry** | ✅ built-in | ✅ built-in | ✅ limited | ✅ built-in | ❌ |
| **Cron scheduling** | ✅ | ✅ (Celery Beat) | ✅ | ✅ | ❌ |
| **Status tracking** | ✅ | ✅ (Flower) | ❌ | ✅ | ❌ |
| **Complexity** | Low | High | Low | Medium | Zero |
| **Performance (20k jobs)** | ~2.5s | ~3.0s | ~4.5s | ~2.0s | N/A (no queue) |
| **Lines of code** | ~700 | ~100k+ | ~3k | ~5k | N/A |
| **Ecosystem** | 3k★, 1.2k users | 25k★, massive | 5k★ | 4k★ | built-in |
| **Maintenance** | Maintenance only | Active | Active | Active | built-in |

> Source benchmark: Steven Yue — "Exploring Python Task Queue Libraries with Load Test" (2024), 20k no-op jobs with 10 workers via Redis.

### When to Choose ARQ

- **100% async stack** (FastAPI + asyncio) — ARQ is the most natural choice
- **Redis is already in the company's ecosystem**
- **Simplicity is needed** — 700 lines vs 100k+ of Celery
- **I/O-bound jobs** (download, parsing, external APIs) — where asyncio shines
- **Tight resource budget** — ARQ runs in lightweight processes without forking

### When to Avoid ARQ

- **Project in maintenance-only mode** — no guarantee of new features
- **Need RabbitMQ/SQS** — ARQ only supports Redis as broker
- **Heavy CPU-bound jobs** — asyncio does not help CPU-bound tasks; better use Celery with prefork or Dramatiq
- **Need complex workflows** (group/chord/canvas from Celery) — ARQ has no DAG primitives
- **Team already has Celery expertise** — migration may not be worth the cost
