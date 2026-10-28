---
date: 2026-06-30
topic: Alembic
tags: [database, migrations, sqlalchemy, postgresql, sqlite, schema, ddl]
sources:
  - title: "Alembic Official Tutorial — 1.18.5"
    url: "https://alembic.sqlalchemy.org/en/latest/tutorial.html"
  - title: "Alembic Auto Generating Migrations"
    url: "https://alembic.sqlalchemy.org/en/latest/autogenerate.html"
  - title: "Alembic Cookbook"
    url: "https://alembic.sqlalchemy.org/en/latest/cookbook.html"
  - title: "Running Batch Migrations for SQLite"
    url: "https://alembic.sqlalchemy.org/en/latest/batch.html"
  - title: "Working with Branches"
    url: "https://alembic.sqlalchemy.org/en/latest/branches.html"
  - title: "Alembic — Database Migration with SQLAlchemy (IceBear Blog 2026)"
    url: "https://ice-ice-bear.github.io/posts/2026-02-24-alembic-database-migration/"
  - title: "Alembic + SQLAlchemy: Migration Best Practices That Won't Break Production (Medium 2026)"
    url: "https://medium.com/@ygsh0816/alembic-sqlalchemy-migration-best-practices-that-wont-break-production-09cc2f417715"
  - title: "Best Practices for Alembic and SQLAlchemy (DEV Community 2024)"
    url: "https://dev.to/welel/best-practices-for-alembic-and-sqlalchemy-3b34"
---

# Alembic — Versioned Migrations for Audime

## What is Alembic

**Alembic** is a database migration tool created by Mike Bayer (also the creator of SQLAlchemy). It enables versioning schema (DDL) changes as code, allowing you to:

- Create migrations that transform the current schema into a new state
- Safely revert (downgrade) migrations
- Automatically generate migrations by comparing your SQLAlchemy models against the real database (autogenerate)
- Maintain a complete history of all schema changes
- Work as a team without schema conflicts

### Core Concepts

| Concept | Description |
|---------|-------------|
| **Migration** | Python script with `upgrade()` and `downgrade()` functions |
| **Revision** | Unique identifier (partial hash) for each migration |
| `down_revision` | Pointer to the previous migration — forms a chain |
| **Head** | Latest migration in the chain |
| **Base** | First migration (down_revision = None) |
| **`alembic_version`** | Table storing the current revision of the database |
| **Autogenerate** | Automatically generate a migration from the diff between models and the database |
| **Branch** | Branching point when two migrations share the same down_revision |
| **Merge** | Migration that joins two branches |

### Standard Workflow

```bash
# 1. Initialize migration environment
alembic init alembic

# 2. Configure alembic.ini and env.py (see sections below)

# 3. Create a manual migration
alembic revision -m "description"

# 4. OR generate automatically (autogenerate)
alembic revision --autogenerate -m "description"

# 5. Apply the migration
alembic upgrade head

# 6. Revert the last migration
alembic downgrade -1

# 7. Check status
alembic current
alembic history
alembic heads
```

### What Autogenerate Detects (and What It Does NOT Detect)

**Detects:**
- Table creation/removal
- Column addition/removal
- Column nullable changes
- Basic changes in named indexes and unique constraints
- Basic foreign key changes
- Type changes (if `compare_type=True`, which is default since 1.12)
- Server default changes (if `compare_server_default=True`)

**Does NOT detect (requires manual editing):**
- Table renames (sees as drop + create)
- Column renames (sees as drop + add — **dangerous**, may lose data)
- Anonymous constraints (unnamed)
- Enum types — requires `alembic-postgresql-enum` extension
- Sequences, triggers, views, stored procedures
- CHECK constraint changes

> ⚠️ **Golden rule:** autogenerate is a **starting point**. Always manually review the generated script before applying.

---

## How Versioning Works

Each migration contains:

```python
"""description

Revision ID: abc123def456
Revises: xyz789abc000
Create Date: 2026-06-30 10:00:00.000000
"""
revision = 'abc123def456'
down_revision = 'xyz789abc000'   # None for the first migration

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('usuario', sa.Column('idade', sa.Integer))

def downgrade():
    op.drop_column('usuario', 'idade')
```

Alembic uses a **linked chain** (`down_revision`) to determine order. The `alembic_version` table in the database stores the current revision. When you run `alembic upgrade head`, it calculates the path from the current revision to the head and executes each intermediate migration.
