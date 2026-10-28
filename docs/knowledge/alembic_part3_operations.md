# Alembic Part 3: Operations, Best Practices, and Risks

## 4. Initial Migration — "Baseline" or "Stamping"

Since Audime already has a running PostgreSQL database with tables created, we need to create a **baseline migration** (migration 000) that simply "stamps" the current schema as head, without executing DDL.

**Recommended approach:**

#### Option A: Stamp (recommended — no data loss risk)

```bash
# First, connect to the target PostgreSQL database
export ALEMBIC_DB_DRIVER=postgresql

# Create an empty migration to serve as base
alembic revision -m "initial_schema_baseline"
```

Edit the generated file in `alembic/versions/` so that `upgrade()` and `downgrade()` are **empty** (just `pass`). This is because the database is already in the desired state.

Then, **stamp** the existing database as if it were at head:

```bash
alembic stamp head
```

This only inserts a record into the `alembic_version` table, without altering anything in the database.

#### Option B: Migration with create_all (for empty environments)

If starting from scratch (e.g., CI, new dev), create a migration that calls `Base.metadata.create_all()`:

```python
"""create all tables

Revision ID: 00000001
Revises: None
Create Date: 2026-06-30
"""
revision = '00000001'
down_revision = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.execute("CREATE SCHEMA IF NOT EXISTS raw")
    op.execute("CREATE SCHEMA IF NOT EXISTS core")
    op.execute("CREATE SCHEMA IF NOT EXISTS staging")
    op.execute("CREATE SCHEMA IF NOT EXISTS analytics")
    op.execute("""
        CREATE TYPE core.extracao_status AS ENUM (
            'PENDING', 'RUNNING', 'DONE', 'ERROR'
        )
    """)

def downgrade():
    op.execute("DROP TYPE IF EXISTS core.extracao_status")
    op.execute("DROP SCHEMA IF EXISTS analytics CASCADE")
    op.execute("DROP SCHEMA IF EXISTS staging CASCADE")
    op.execute("DROP SCHEMA IF EXISTS core CASCADE")
    op.execute("DROP SCHEMA IF EXISTS raw CASCADE")
```

> **Recommendation:** use **Option A (stamp)** for the existing database. For new setups (dev/CI), create a separate script (`scripts/create_db.py`) that runs `Base.metadata.create_all(engine)` and then `alembic stamp head`, following the Cookbook recipe.

---

## 5. How to Run Migrations

```bash
# ========== PostgreSQL (production/dev) ==========

export ALEMBIC_DB_DRIVER=postgresql   # optional, it is the default

# Check current status
alembic current

# View history
alembic history

# Apply all pending migrations
alembic upgrade head

# Revert the last migration
alembic downgrade -1

# Revert to a specific revision
alembic downgrade abc123

# Create new migration via autogenerate
alembic revision --autogenerate -m "add_column_x_to_y"

# Check for pending changes (CI)
alembic check


# ========== SQLite (tests) ==========

export ALEMBIC_DB_DRIVER=sqlite
export ALEMBIC_DB_URL=sqlite:///./test.db

alembic upgrade head
alembic downgrade -1
```

---

## 6. Transition Strategy: From `scripts.sql` to Versioned Migrations

**Step 1 — Create the baseline:**

```bash
alembic init alembic
# Configure env.py (as above)
alembic revision -m "baseline_schema"
# Edit the migration: upgrade() and downgrade() empty
alembic stamp head
```

This creates the `alembic_version` table in the existing database and records the revision, without altering anything.

**Step 2 — Migrate `scripts.sql`:**

The `scripts.sql` contains DDL that is already applied to the database. What is NOT in the database (e.g., column `qtd_total_itens` and constraint `uq_nota_chave_usuario`) should already be applied. Verify that the database reflects `scripts.sql` exactly. After stamping, the database is "synchronized".

**Step 3 — Future changes:**

For any future schema change, instead of editing `scripts.sql`, do:

```bash
alembic revision --autogenerate -m "description_of_change"
# REVIEW the generated script manually!
alembic upgrade head
```

**Step 4 — Remove `scripts.sql` (optional):**

Keep `scripts.sql` as documentation of the initial state, but mark it as `deprecated`. Versioned migrations become the source of truth going forward.

---

## 7. Day-to-Day Useful Commands

```bash
# === Creation ===
alembic revision -m "description"                    # manual
alembic revision --autogenerate -m "description"     # automatic

# === Application ===
alembic upgrade head                                 # apply everything
alembic upgrade +1                                   # advance by 1
alembic upgrade abc123                               # up to specific revision

# === Reversal ===
alembic downgrade -1                                 # back 1
alembic downgrade abc123                             # down to specific revision
alembic downgrade base                               # back to the beginning

# === Information ===
alembic current                                      # where am I
alembic history                                      # entire history
alembic history -r-3:current                         # last 3
alembic heads                                        # current heads
alembic branches                                     # branches (if any)

# === CI ===
alembic check                                        # detects unmigrated changes

# === Offline ===
alembic upgrade head --sql > upgrade.sql             # generate SQL for DBA
```
