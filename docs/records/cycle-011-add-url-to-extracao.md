# Cycle 11 — Adicionar coluna url na tabela core.extracao (Issue #11)

**Date:** 2026-07-05
**Agent:** scrum_master (full sprint cycle)
**Status:** ✅ 16/16 criteria approved (0 FAIL)

---

## What was implemented

### Backend: Add `url` column to `Extracao` model

1. **Model** (`abstract/models/core.py`): Added `url = sa.Column(sa.Text, nullable=True)` column to `Extracao`. Also fixed `id_extracao` with `with_variant(sa.Integer(), "sqlite")` for SQLite autoincrement compatibility (pre-existing bug discovered during TDD).

2. **Migration** (`alembic/versions/8a3f7e2c9d1b_add_url_to_extracao.py`): New Alembic revision that:
   - Upgrade: Adds `url TEXT` column to `extracao` (PostgreSQL: schema `core`, SQLite: no schema)
   - Downgrade: Drops the `url` column
   - Idempotent: checks if column exists before adding/dropping
   - Compatible with both PostgreSQL and SQLite via `schema_translate_map`

3. **Schemas** (`app/api/v1/schemas.py`): Added `url: Optional[str] = None` to all three response schemas:
   - `ExtracaoResponse`
   - `ExtracaoStatusResponse`
   - `ExtracaoJobResponse`

4. **API Endpoint** (`app/api/v1/endpoints/extracoes.py`): Changed `Extracao()` constructor to save `url=str(body.url)`. Also fixed the `obter_status_extracao` response to return the actual `url` from the database.

### Frontend: Modal with extraction details

5. **API Client** (`web/src/api/extracoes.ts`): Added `url?: string` to `ExtracaoResult` interface.

6. **Component** (`web/src/pages/Extrair.tsx`):
   - Added `modalExtracao` state and clickable rows with `onClick`/keyboard support
   - Modal dialog displays: Extraction ID, Status (badge), Creation date, URL (clickable hyperlink)
   - Modal closes via close button or overlay click (`e.stopPropagation()` on content)
   - Polling continues independently — modal does not interfere with the polling lifecycle

7. **Styles** (`web/src/pages/Extrair.module.css`): Added `.modalOverlay`, `.modal`, `.modalClose`, `.modalTitle`, `.modalDetails`, `.modalUrl`, `.tableRow:hover` styles.

### Tests (TDD)

8. **New test file** (`tests/test_extracao_url.py`): 3 tests:
   - `test_create_extracao_saves_url` — POST saves URL, GET list returns it
   - `test_get_extracao_by_id_returns_url` — GET by id returns URL
   - `test_url_nullable_for_old_records` — Records without URL return `null`

9. **Migration test** (`tests/test_migrations.py`): Added `test_migration_adds_url_column_to_extracao`.

10. **Existing test update** (`tests/test_extracao_flow.py`): Added `assert "url" in d` assertions.

---

## Validation results

### ✅ 16 PASS

| Criterion | Description | Status |
|-----------|-------------|--------|
| CAT-001 | Model `url` column nullable `Text` | ✅ |
| CAT-002 | Migration adds `url` column | ✅ |
| CAT-003 | POST saves `url` | ✅ |
| CAT-004 | `GET /v1/extracoes` returns `url` | ✅ |
| CAT-005 | `GET /v1/extracoes/{id}` returns `url` | ✅ |
| CAT-006 | `GET /v1/extracoes/{id}/status` returns `url` | ✅ |
| CAT-007 | Schemas updated with `url` | ✅ |
| CAT-008 | Frontend `ExtracaoResult` includes `url?: string` | ✅ |
| CAT-009 | Modal opens on click with URL link | ✅ |
| CAT-010 | Polling continues with modal open | ✅ |
| CAT-011 | No regression (all existing tests pass) | ✅ |
| CAT-012 | Test: POST saves URL | ✅ |
| CAT-013 | Test: URL nullable for old records | ✅ |
| CAT-014 | Migration test: upgrade adds url column | ✅ |
| CAT-015 | TypeScript compiles without errors | ✅ |
| CAT-016 | No leaked credentials | ✅ |

### Tests

```
python -m pytest tests/ -v -> 44 passed (3.01s)
  tests/test_auth_flow.py         3 passed
  tests/test_extracao_flow.py     4 passed
  tests/test_extracao_url.py      3 passed  (NEW)
  tests/test_migrations.py        6 passed  (1 NEW)
  tests/test_parser_nfce.py      28 passed
```

TypeScript compilation: `npx tsc --noEmit` — zero errors ✅

### Security

No leaked credentials. DevOps scan: **APPROVED** ✅
- All 10 changed/new files free of credential leaks
- `.env` properly gitignored
- No hardcoded secrets in code

---

## Technical decisions

### Nullable vs NOT NULL
Chose `nullable=True` over `nullable=False` because:
1. Existing extractions in the database have no URL — making it NOT NULL would require a two-step migration (add nullable → backfill → alter to NOT NULL)
2. Semantically correct: `NULL` means "URL was not collected" vs empty string `""` which is ambiguous
3. Future sprint can add NOT NULL after backfilling old records

### Idempotent migration
The migration uses `inspect()` to check if the `url` column already exists before adding/dropping. This is required because `test_upgrade_idempotent` runs `upgrade("head")` twice.

### SQLite schema handling
The migration uses `_is_sqlite()` and conditional `schema=None` for SQLite compatibility — following the same pattern as the existing `9ae2f5b1c3d4` migration.

### HttpUrl → str conversion
`body.url` is `HttpUrl` (Pydantic type). Used explicit `str(body.url)` in the Extracao constructor to avoid ambiguity with different database drivers.

### Pre-existing bug fix
During TDD, discovered that `Extracao.id_extracao` used `sa.BigInteger` without `with_variant(sa.Integer(), "sqlite")`, causing SQLite to fail autoincrement. Applied the same fix that `Usuario.id_usuario` already had. No migration needed — the PostgreSQL DDL is unchanged.

---

## Files changed

| File | Change |
|------|--------|
| `abstract/models/core.py` | Added `url` column + fixed `id_extracao` SQLite variant |
| `alembic/versions/8a3f7e2c9d1b_add_url_to_extracao.py` | **NEW** — Migration |
| `app/api/v1/schemas.py` | Added `url: Optional[str] = None` to 3 schemas |
| `app/api/v1/endpoints/extracoes.py` | Save `url` on POST, return `url` in status endpoint |
| `tests/test_extracao_url.py` | **NEW** — 3 TDD tests for url field |
| `tests/test_migrations.py` | Added migration column test |
| `tests/test_extracao_flow.py` | Added `url` field assertions |
| `web/src/api/extracoes.ts` | Added `url?: string` to interface |
| `web/src/pages/Extrair.tsx` | Added modal with clickable rows |
| `web/src/pages/Extrair.module.css` | Added modal and hover styles |

---

## Pending items

### Add linter to project
No Python linter (ruff, flake8) is configured. Adding one would improve code quality enforcement. Priority: LOW

### Tab visibility for polling
The polling interval continues when the browser tab is hidden. Using the Page Visibility API to pause/resume polling would save bandwidth. Priority: LOW

---

## Lessons learned

### SQLite BIGINT autoincrement
SQLite only auto-increments `INTEGER PRIMARY KEY` columns, not `BIGINT PRIMARY KEY`. For SQLAlchemy models in dual-dialect projects, always use `sa.BigInteger().with_variant(sa.Integer(), "sqlite")` for primary keys. [CONSTRAINT]

### TDD reveals pre-existing bugs
Writing tests for the new `url` field exposed a pre-existing bug where `id_extracoa` lacked SQLite autoincrement compatibility. Without TDD, this bug would have surfaced later as a confusing test failure. [EXECUTION]

### Explicit response field population
When adding a field to a Pydantic response schema with `from_attributes=True`, the field is populated automatically when returning ORM objects directly. However, when constructing the response manually (like in `obter_status_extracao`), the field must be explicitly passed. [MEMORY]
