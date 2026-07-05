# Sprint Record: Soft Delete (Desativação) de Notas no Analytics

**Date**: 2026-07-05
**Sprint Lead**: scrum_master

---

## Summary

Implemented soft delete (desativação) for analytics notas via `is_active` boolean column. Users can now deactivate notas from the detail page, hiding them from the dashboard without deleting data.

## Changes

### Model
- `abstract/models/analytics.py`: Added `is_active = sa.Column(sa.Boolean, nullable=False, default=True)` to `NotaAnalytics`

### Migration
- `alembic/versions/ea7f3d2b1c5a_add_is_active_to_nota_analytics.py`: Adds `is_active` column with `server_default=true` (PG) / `"1"` (SQLite)

### API (Backend)
- `app/api/v1/schemas.py`: Added `is_active: bool = True` to `DashboardNotaResponse`, added `NotaPatchRequest(BaseModel)`
- `app/api/v1/endpoints/dashboard.py`:
  - `GET /v1/dashboard/notas`: Added `NotaAnalytics.is_active == True` to subquery filter
  - `GET /v1/dashboard/notas/{id_extracao}`: Added `NotaAnalytics.is_active == True` filter
  - `PATCH /v1/dashboard/notas/{id_extracao}`: New endpoint (toggle via `{"is_active": bool}`)
  - `_build_from_analytics`: Added `is_active` to response

### Frontend
- `web/src/types/index.ts`: Added `is_active: boolean` to `DashboardNota` interface
- `web/src/api/dashboard.ts`: Added `desativarNota(idExtracao, isActive)` calling `api.patch()`
- `web/src/pages/NotaDetalhe.tsx`: Added "Desativar Nota" / "Reativar Nota" button with loading state and success/error message
- `web/src/pages/NotaDetalhe.module.css`: Added styles for actions, buttons, success/error messages

### Tests
- `tests/test_dashboard.py`: Added `TestSoftDelete` class with 12 tests covering:
  - Model column existence and default
  - List filtering (active/inactive)
  - Individual GET (404 for inactive)
  - Historico (shows inactive)
  - PATCH desativar/reativar
  - Idempotency
  - Auth guard (wrong user → 404)
  - Non-existent (404)
  - Same chave mixed active/inactive

## Results

| Metric | Value |
|--------|-------|
| Tests added | 12 |
| Tests passed | 54 (+12 new) |
| Tests xfailed | 8 (unchanged) |
| Tests xpassed | 2 (unchanged) |
| Frontend build | ✅ Clean (tsc + vite) |
| Security audit | ✅ No leaks |

## Key Decisions

1. **Column name**: `is_active` (English, consistent with `is_current`) — per product_manager and tech_lead recommendations
2. **API design**: `PATCH /v1/dashboard/notas/{id}` with body `{"is_active": bool}` (RESTful toggle pattern) — supports both deactivation and reactivation
3. **No SCD2 inheritance**: New rows created by `transformar_extracao` default to `is_active=True`. Deactivation is per-extraction, not per-chave. This avoids coupling soft-delete with the transform pipeline
4. **Historico unfiltered**: Users can always see full version history of deactivated notas
5. **No index added**: At current scale (~6k rows), partial index is premature optimization

## Files Changed

| File | Action |
|------|--------|
| `abstract/models/analytics.py` | Modified (add `is_active` column) |
| `alembic/versions/ea7f3d2b1c5a_add_is_active_to_nota_analytics.py` | Added (migration) |
| `app/api/v1/schemas.py` | Modified (add `is_active` to response, `NotaPatchRequest`) |
| `app/api/v1/endpoints/dashboard.py` | Modified (filters + PATCH endpoint) |
| `tests/test_dashboard.py` | Modified (12 new tests) |
| `web/src/types/index.ts` | Modified (add `is_active` to type) |
| `web/src/api/dashboard.ts` | Modified (add `desativarNota`) |
| `web/src/pages/NotaDetalhe.tsx` | Modified (add toggle button) |
| `web/src/pages/NotaDetalhe.module.css` | Modified (add button/message styles) |

## Lessons Learned

- The TDD approach (write all tests first, then implement) caught a missing edge case: the PATCH endpoint needed to filter by `id_usuario` for auth, which was identified while writing the `test_patch_wrong_user_returns_404` test
- Discovery phase (product_manager + tech_lead) was valuable for catching the naming inconsistency (`ativo` vs `is_active`) before implementation
- The existing `api.patch()` method in the frontend client already existed, making the frontend implementation straightforward
