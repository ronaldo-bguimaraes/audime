# Migrações com Alembic

O Audime usa [Alembic](https://alembic.sqlalchemy.org/) para versionar mudanças no schema do banco de dados. Este documento descreve os comandos básicos e boas práticas.

## Setup

As migrações estão configuradas em:

- `alembic.ini` — configuração geral (raiz do projeto)
- `alembic/env.py` — configuração do ambiente (importa modelos, conecta ao banco)
- `alembic/versions/` — scripts de migração versionados

A URL de conexão é resolvida na seguinte ordem de precedência:

1. `ALEMBIC_DB_URL` (variável de ambiente)
2. `app.core.config.Settings` (PostgreSQL em produção)
3. `sqlite:///./test.db` (fallback para desenvolvimento/testes)

## Comandos Básicos

### Aplicar migrações

```bash
# Aplica todas as migrações pendentes
alembic upgrade head

# Aplica 1 migração
alembic upgrade +1

# Aplica até uma revisão específica
alembic upgrade <revision_hash>
```

### Reverter migrações

```bash
# Reverte a última migração
alembic downgrade -1

# Reverte até uma revisão específica
alembic downgrade <revision_hash>

# Reverte até o início (base)
alembic downgrade base
```

### Verificar status

```bash
# Versão atual
alembic current

# Histórico completo
alembic history

# Últimas 3 migrações
alembic history -r-3:current

# Heads atuais
alembic heads
```

### Criar novas migrações

```bash
# Automática (compara modelos com banco)
alembic revision --autogenerate -m "descricao_da_mudanca"

# Manual
alembic revision -m "descricao_da_mudanca"
```

> ⚠️ **Importante**: Sempre revise o script gerado por `--autogenerate` antes de aplicar. O autogenerate não detecta renomeações de colunas/tabelas (detecta como drop + create), não gerencia ENUMs PostgreSQL, e pode gerar operações incorretas para foreign keys entre schemas.

### Verificar se o schema está sincronizado (CI)

```bash
# Aplica migrações e verifica
alembic upgrade head
alembic check
```

O comando `alembic check` compara o schema do banco com os modelos SQLAlchemy. Se houver diferenças, retorna exit code != 0.

> **Nota**: `alembic check` só funciona com precisão contra PostgreSQL. Em SQLite, diferenças de tipo (BIGINT vs INTEGER, JSONB vs JSON, ENUMs) geram falsos positivos.

### Gerar SQL sem aplicar (modo offline)

```bash
alembic upgrade head --sql > upgrade.sql
alembic downgrade -1 --sql > downgrade.sql
```

## PostgreSQL vs SQLite

| Aspecto | PostgreSQL | SQLite |
|---------|-----------|--------|
| **Schemas** | `raw`, `core`, `staging`, `analytics` | Traduzidos para `None` via `schema_translate_map` |
| **Tipos** | `BIGINT`, `JSONB`, `TIMESTAMPTZ`, ENUMs | `INTEGER`, `JSON`, `TIMESTAMP`, VARCHAR+CHECK |
| **Migrations** | Produção e desenvolvimento | Apenas testes |
| **`--autogenerate`** | ✅ Recomendado | ❌ **Nunca usar** — gera migrações perigosas |
| **`alembic check`** | ✅ Preciso | ⚠️ Falsos positivos em tipos |
| **`alembic upgrade`** | ✅ Transacional | ⚠️ Não transacional (DDL implícito) |

### Para testes (SQLite)

```bash
export ALEMBIC_DB_URL=sqlite:///./test.db
alembic upgrade head
alembic downgrade -1
```

### Para produção/dev (PostgreSQL)

```bash
# A URL é lida das settings do projeto (.env)
alembic upgrade head
alembic check
```

## Migration Inicial (Stamp)

A migration inicial (`8f830e7a6053_initial_schema.py`) é **vazia** (upgrade/downgrade = `pass`). Ela serve como "stamp" — marca que o banco existente já está no estado correto.

**Por que vazia?** O Audime já tem as tabelas criadas em produção via `scripts.sql`. O `Base.metadata` (modelos SQLAlchemy) é a fonte da verdade para o schema declarativo. Migrações futuras usarão `--autogenerate` a partir deste baseline.

**Para ambientes novos** (dev, CI sem banco existente), o setup é:

```bash
# 1. Cria todas as tabelas via SQLAlchemy (equivalente ao scripts.sql)
#    Configure a env var ALEMBIC_DB_URL antes ou use Settings do .env
python3 -c "
import os
from sqlalchemy import create_engine
from abstract.base import Base
from abstract.models import *  # noqa

db_url = os.environ.get('ALEMBIC_DB_URL', 'postgresql+psycopg://<usuario>:<senha>@localhost/audime')
engine = create_engine(db_url)
Base.metadata.create_all(bind=engine)
"

# 2. Stampa como head (marca que o schema está atualizado)
alembic stamp head
```

## scripts.sql

O arquivo `scripts.sql` na raiz do projeto contém o DDL histórico das migrations manuais. Ele é mantido como documentação de referência, mas **não é mais a fonte da verdade** para o schema — essa função foi assumida pelas migrações versionadas do Alembic e pelos modelos SQLAlchemy.

## Boas Práticas

1. **Sempre revise migrations geradas por autogenerate** — ele não entende intenção (rename vs drop+add)
2. **Sempre escreva o `downgrade()`** — mesmo que complexo, é essencial para rollback seguro
3. **Commite migrations no Git junto com as mudanças nos modelos** — para que estejam sempre sincronizadas
4. **Teste migrations em SQLite primeiro** (upgrade/downgrade), depois PostgreSQL
5. **Mantenha migrations pequenas e focadas** — uma mudança por migration
6. **Nunca edite migrations já aplicadas em produção** — crie uma nova migration
7. **Nunca rode `--autogenerate` contra SQLite** — use sempre PostgreSQL
8. **Inclua `alembic check` no CI** com PostgreSQL para detectar schemas desalinhados

## Resumo Rápido

```bash
# Desenvolvimento
alembic upgrade head                    # aplicar
alembic revision --autogenerate -m "x"  # nova migration
alembic downgrade -1                    # reverter

# CI
alembic upgrade head && alembic check

# Info
alembic current
alembic history
```
