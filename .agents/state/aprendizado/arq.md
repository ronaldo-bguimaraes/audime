---
date: 2026-06-30
topic: ARQ — Async Redis Queue para gerenciamento de filas de tarefas
tags: [arq, task-queue, async, redis, background-jobs, fastapi]
sources:
  - title: ARQ Documentation (v0.28.0)
    url: https://arq-docs.helpmanual.io/
  - title: ARQ GitHub Repository (python-arq/arq)
    url: https://github.com/python-arq/arq
  - title: "Managing Background Tasks in FastAPI: BackgroundTasks vs ARQ + Redis" — David Muraya
    url: https://davidmuraya.com/blog/fastapi-background-tasks-arq-vs-built-in
  - title: "Task Queues — Durable Background Jobs with ARQ and Redis" — StackLesson
    url: https://www.stacklesson.com/react-fastapi/fastapi-uploads-tasks/ch30-lesson-04-task-queues-with-arq/
  - title: "Celery Versus ARQ: Choosing the Right Task Queue for Python Applications" — Leapcell
    url: https://leapcell.io/blog/celery-versus-arq-choosing-the-right-task-queue-for-python-applications
  - title: "Exploring Python Task Queue Libraries with Load Test" — Steven Yue
    url: https://stevenyue.com/blogs/exploring-python-task-queue-libraries-with-load-test
  - title: "Python Task Queue Libraries Compared" — StudyRaid
    url: https://app.studyraid.com/en/read/15008/518850/celery-vs-other-task-queue-systems
  - title: FastAPI-ARQ Reference Project — davidmuraya/fastapi-arq
    url: https://github.com/davidmuraya/fastapi-arq
---

# ARQ — Async Redis Queue — 2026-06-30

## O que é

**ARQ** (Async Redis Queue) é uma biblioteca Python para filas de tarefas assíncronas construída sobre Redis e asyncio. Criada por Samuel Colvin (mesmo criador do Pydantic), ARQ foi concebida como sucessora moderna e performática do RQ.

**Versão atual:** v0.28.0 (Abril/2026) — suporta Python 3.9 a 3.14.
**Status do projeto:** *Maintenance only mode* ([issue #510](https://github.com/python-arq/arq/issues/510)) — está estável e maduro, sem novas features planejadas, mas com manutenção ativa.

### Arquitetura

ARQ funciona com três componentes:

1. **Produtor** (sua app FastAPI): enfileira jobs chamando `redis.enqueue_job('nome_da_funcao', args...)`
2. **Redis**: atua como broker e backend de resultados (usa listas, hashes e sorted sets)
3. **Worker** (processo separado): executa `arq app.WorkerSettings`, escuta a fila e processa jobs

### Características principais

| Característica | Descrição |
|---|---|
| **Totalmente async** | Construído sobre asyncio — jobs são `async def`, sem forking |
| **Execução pessimista** | Jobs não são removidos da fila até sucederem ou falharem definitivamente. Se o worker cair, o job é requeitado automaticamente |
| **Retry embutido** | `raise Retry(defer=N)` para retentar com backoff; `max_tries` configura o limite |
| **Agendamento** | `_defer_by` / `_defer_until` para execução futura; `cron()` para jobs periódicos |
| **Job ID único** | `_job_id` customizável garante uniquidade na fila (transação Redis) |
| **Resultados** | `job.result(timeout=N)` para aguardar; `job.status()` para polling |
| **Múltiplas filas** | Suporte a `queue_name` para separar prioridades |
| **Hooks** | `on_startup`, `on_shutdown`, `on_job_start`, `on_job_end` |
| **Health check** | Worker registra heartbeat no Redis a cada `health_check_interval` |
| **Serialização** | Pickle por padrão; customizável (MsgPack, JSON, etc.) |
| **Tamanho** | ~700 linhas de código — pequeno, focado, fácil de debugar |

## Quando usar ARQ vs alternativas

| Critério | ARQ | Celery | Huey | Dramatiq | FastAPI BackgroundTasks |
|---|---|---|---|---|---|
| **Async-first** | ✅ nativo | ⚠️ possível com aio-celery | ❌ síncrono | ✅ threads | ✅ nativo |
| **Broker** | Redis only | RabbitMQ, Redis, SQS | Redis, SQLite | Redis, RabbitMQ | Nenhum (mesmo processo) |
| **Persistência** | ✅ Redis | ✅ broker | ✅ Redis | ✅ broker | ❌ volatil |
| **Retry** | ✅ embutido | ✅ embutido | ✅ limitado | ✅ embutido | ❌ |
| **Agendamento cron** | ✅ | ✅ (Celery Beat) | ✅ | ✅ | ❌ |
| **Tracking de status** | ✅ | ✅ (Flower) | ❌ | ✅ | ❌ |
| **Complexidade** | Baixa | Alta | Baixa | Média | Zero |
| **Performance (20k jobs)** | ~2.5s | ~3.0s | ~4.5s | ~2.0s | N/A (no queue) |
| **Linhas de código** | ~700 | ~100k+ | ~3k | ~5k | N/A |
| **Ecosystem** | 3k★, 1.2k users | 25k★, massivo | 5k★ | 4k★ | built-in |
| **Maintenance** | Maintenance only | Ativo | Ativo | Ativo | built-in |

> Fonte benchmark: Steven Yue — "Exploring Python Task Queue Libraries with Load Test" (2024), 20k no-op jobs com 10 workers via Redis.

### Quando escolher ARQ

- **Stack 100% async** (FastAPI + asyncio) — ARQ é a escolha mais natural
- **Redis já está no ecossistema** da empresa
- **Precisa de simplicidade** — 700 linhas vs 100k+ do Celery
- **Jobs I/O-bound** (download, parsing, APIs externas) — onde asyncio brilha
- **Orçamento de recursos enxuto** — ARQ roda em processos leves sem fork

### Quando evitar ARQ

- **Projeto em maintenance-only mode** — sem garantia de novas features
- **Precisa de RabbitMQ/SQS** — ARQ só suporta Redis como broker
- **Jobs CPU-bound pesados** — asyncio não ajuda CPU-bound; melhor usar Celery com prefork ou Dramatiq
- **Precisa de workflows complexos** (group/chord/canvas do Celery) — ARQ não tem primitivas de DAG
- **Equipe já tem expertise em Celery** — a migração pode não valer o custo

## Para que usaríamos no Audime

### O gargalo principal: extração NFC-e síncrona

O endpoint `POST /v1/extracoes` (em `app/api/v1/endpoints/extracoes.py`) executa **sincronamente** a função `executar_extracao()` em `app/services/extracao_service.py`. O fluxo atual:

```
POST /v1/extracoes → download_url() → upload_to_r2() → parse_nfce() → INSERTs no DB → response
```

Isso bloqueia o worker do Uvicorn durante todo o processo (download + parse + writes). Se a URL estiver lenta, se o SEFAZ demorar, se o parse falhar — o cliente fica esperando. Pior: se o worker reiniciar, a extração é perdida.

### Onde ARQ se encaixaria

1. **Endpoint vira produtor**: `POST /v1/extracoes` enfileira um job ARQ e retorna `{ "job_id": "...", "status": "queued" }` imediatamente (HTTP 202 Accepted)
2. **Worker ARQ processa em background**: faz o download, upload, parse, e persistência
3. **Cliente polla o resultado**: `GET /v1/extracoes/{id_extracao}/status` consulta o status no DB + Redis
4. **Resiliência**: se o worker cair durante o processamento, o job é requeitado automaticamente (execução pessimista)

### Impacto no Docker Compose

```yaml
# NOVO: serviço Redis
redis:
  image: redis:7-alpine
  container_name: audime-redis
  restart: unless-stopped
  ports:
    - "${REDIS_PORT:-6379}:6379"
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 5s

# NOVO: serviço worker ARQ
worker:
  build: .
  container_name: audime-worker
  restart: unless-stopped
  command: arq app.workers.arq_settings.WorkerSettings
  environment:
    # mesmas envs do backend + REDIS_HOST
    REDIS_HOST: redis
    DB_POSTGRES_HOST: postgres
    # ... demais envs
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_started
```

### Impacto nas dependências

```toml
# pyproject.toml — adicionar
dependencies = [
    # ... existentes
    "arq>=0.28.0",
    "redis[hiredis]>=4.2.0,<6",  # transitiva do arq
]

# ou via pip:
# pip install arq
```

### Impacto na configuração

```python
# app/core/config.py — adicionar
class Settings(BaseSettings):
    # ... existentes
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str | None = None
    redis_db: int = 1  # separado do cache, se houver
```

### Como o endpoint mudaria (exemplo conceitual — NÃO implementado)

```python
# app/api/v1/endpoints/extracoes.py — REFATORADO
from fastapi import APIRouter, Depends, HTTPException, status
from arq.connections import ArqRedis

router = APIRouter(prefix="/v1/extracoes", tags=["extracoes"])

@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def criar_extracao(
    body: ExtracaoRequest,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_current_user_id),
    arq: ArqRedis = Depends(get_arq_pool),  # dependência customizada
):
    # 1. Cria registro de extração com status PENDING
    extracao = Extracao(id_usuario=id_usuario, status=ExtracaoStatus.PENDING)
    db.add(extracao)
    db.commit()

    # 2. Enfileira job ARQ (passa só IDs — nunca objetos SQLAlchemy!)
    job = await arq.enqueue_job(
        "executar_extracao",
        url=body.url,
        id_extracao=extracao.id_extracao,
        id_usuario=id_usuario,
        _job_id=f"extracao:{extracao.id_extracao}",  # uniquidade garantida
        _defer_by=0,  # executa o mais rápido possível
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

### Como a task ARQ ficaria (exemplo conceitual)

```python
# app/workers/tasks.py — NOVO ARQUIVO
"""Task functions executadas pelo worker ARQ."""

from httpx import AsyncClient  # requests → httpx para async
from app.services.parser_nfce import parse_nfce
from app.services.storage_service import generate_filename, hash_sha256

OUTPUT_PREFIX = "imports/html"

async def executar_extracao(ctx: dict, url: str, id_extracao: int, id_usuario: int):
    """Worker function: download, upload, parse, persist."""
    db_session_factory = ctx["db_session_factory"]
    r2_client = ctx["r2_client"]

    with db_session_factory() as db:
        from abstract.models.core import Extracao, ExtracaoStatus
        from abstract.models.raw import Importacao, ItemNota, Nota
        import posixpath

        try:
            # Atualiza status
            extracao = db.get(Extracao, id_extracao)
            extracao.status = ExtracaoStatus.RUNNING
            db.commit()

            # Download via httpx (assíncrono!)
            async with AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                html_bytes = response.content

            sha256 = hash_sha256(html_bytes)
            filename = generate_filename()
            key = posixpath.join(OUTPUT_PREFIX, filename)

            # Upload para R2
            r2_client.put_object(
                Body=html_bytes,
                Bucket=ctx["bucket"],
                Key=key,
                Metadata={"sha256": sha256},
            )

            # Persiste importação + nota + itens (SQLAlchemy síncrono no worker = ok)
            # ... (mesma lógica do executar_extracao atual)

            extracao.status = ExtracaoStatus.DONE
            db.commit()

        except Exception:
            extracao.status = ExtracaoStatus.ERROR
            db.commit()
            raise  # ARQ retenta automaticamente
```

## Por que NÃO usar (riscos e desvantagens)

1. **Maintenance-only mode**: ARQ não receberá novas features. Para um projeto novo, isso é um risco estratégico. Alternativa: Taskiq (mais moderno) ou Celery (mais consolidado).
2. **Redis como dependência**: Adiciona um serviço novo ao stack (mais memória, monitoramento, backup). Contraponto: Redis é maduro, leve (~5MB), e muitas vezes já está no ecossistema.
3. **Jobs chamados mais de uma vez**: A execução pessimista significa que todo job precisa ser **idempotente**. Extração NFC-e é naturalmente idempotente (chave é UNIQUE no DB), mas é um requisito explícito de design.
4. **Serialização pickle**: ARQ usa pickle para serializar jobs por padrão — inseguro para dados de origem não confiável. Mitigação: usar serializador customizado (MsgPack) ou nunca enfileirar dados sensíveis.
5. **DB session no worker**: O worker ARQ roda em processo separado — não pode compartilhar a session do FastAPI. Precisa criar pool próprio no `on_startup`. Já existe `SessionLocal` em `abstract.engine` que pode ser reutilizada.
6. **Complexidade operacional**: Agora você gerencia 2 processos (API + Worker) + Redis. O docker-compose cresce.
7. **Overhead para tarefas simples**: Se a extração NFC-e levar <2s, talvez FastAPI BackgroundTasks seja suficiente. Mas o risco de perder jobs no restart do servidor permanece.

## Prós e Contras

| Prós | Contras |
|---|---|
| Async-first, integração natural com FastAPI | Maintenance-only mode (sem novas features) |
| Código ultra-enxuto (~700 linhas) — fácil de entender | Só suporta Redis como broker |
| Execução pessimista = jobs não são perdidos em crashes | Requer Redis (dependência extra no stack) |
| Retry automático com backoff (+ `raise Retry()`) | Jobs podem rodar mais de uma vez (exige idempotência) |
| Agendamento futuro + cron jobs embutido | Não tem primitivas de workflow (group/chord) |
| Pool de Redis compartilhado via `ctx` | Pickle como serializador padrão (inseguro) |
| CLI `arq` para rodar worker + health check | Projeto relativamente pequeno (comunidade menor que Celery) |
| Performance ~7-40x melhor que RQ | Menos tutoriais e exemplos que Celery |
| Health check nativo via Redis key | |
| Múltiplas filas com prioridade | |

## Alternativas viáveis para o Audime

1. **FastAPI BackgroundTasks** — para tarefas curtas (<5s), sem necessidade de tracking. Não resolve o problema de persistência.
2. **Celery** — o padrão da indústria, suporta múltiplos brokers, workflows complexos. Overhead alto para o escopo do Audime (~100k+ linhas de código Celery).
3. **Taskiq** — alternativa moderna e async-first, sem maintenance mode. Menos madura que ARQ, mas com mais potencial de crescimento.
4. **Dramatiq** — baseado em threads, bom para jobs I/O-bound. Não é async-first como ARQ.
5. **RQ (Redis Queue)** — síncrono, simples, mas bloqueante com asyncio.

## Conclusão

**ARQ é a escolha certa para o Audime hoje.** O projeto usa FastAPI (100% async), Redis é simples de adicionar ao Docker Compose, e a extração NFC-e é um caso de uso clássico de task queue: I/O-bound (download + parse + upload), com necessidade de resiliência (retry em falha de rede), e onde o cliente não precisa esperar a resposta síncrona.

A migração é de baixo risco porque:
- O código de extração (`executar_extracao`) existe e funciona — só precisa ser adaptado para rodar no worker
- O modelo `Extracao` já tem `status` (PENDING → RUNNING → DONE/ERROR) — exatamente o que ARQ precisa
- A chave da NFC-e (UNIQUE) garante idempotência natural
- O diretório `workers/` já existe no projeto — só adicionar `workers/arq_tasks.py`

O ponto de atenção principal é o **maintenance-only mode** do ARQ. Para um MVP, isso é irrelevante. Para um produto de longo prazo, vale monitorar Taskiq como alternativa futura.

> ⚠️ **Nota importante**: ARQ v0.16 teve uma **reescrita completa** que quebrou compatibilidade com código pré-v0.16. Qualquer tutorial ou exemplo anterior a 2019 pode estar desatualizado. Sempre usar documentação da v0.28.
