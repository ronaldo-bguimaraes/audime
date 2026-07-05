# 2026-06-30 — NFC-e Parser Enhancement

## What was done
- Complete rewrite of `app/services/parser_nfce.py`:
  - Extracts CNPJ, address, protocol, payment methods, consumer, environment, taxes, COO, PDV, change
  - `valor_total` read from HTML (not calculated by sum)
  - Key sanitized (spaces removed → 44 chars)
  - Robust `br_to_float()` for BR decimal format (comma, thousands dot, "NaN")
  - Replaced fragile `.contents[1]` with regex + `get_text(strip=True)`
- Added `qtd_total_itens` as column in `Nota` model
- Passes `extra` and `qtd_total_itens` in `extracao_service.py`
- Exposed `extra` and `qtd_total_itens` in `NotaResponse` (Pydantic)
- Added `extra` and `qtd_total_itens` to TypeScript types
- Frontend `NotaDetalhe.tsx` displays: CNPJ, address, protocol, payment methods, taxes, COO, PDV, item count
- Playwright mocks updated with `extra` and `qtd_total_itens`
- SQL migration added in `scripts.sql`

## Modified files
- `app/services/parser_nfce.py` — (+388/-25)
- `abstract/models/raw.py` — +1 column
- `app/services/extracao_service.py` — passes extra + qtd_total_itens
- `app/api/v1/schemas.py` — +2 fields
- `web/src/types/index.ts` — +2 fields
- `web/src/pages/NotaDetalhe.tsx` — new sections
- `web/src/pages/NotaDetalhe.module.css` — .sectionTitle
- `web/tests/fixtures.ts` — updated mocks
- `scripts.sql` — migration

## Criteria met
- [x] C1.1–C1.12: All 12 parser criteria
- [x] C2.1–C2.4: Model and service
- [x] C3.1–C3.2: API Schemas
- [x] C4.1–C4.2: Frontend Types
- [x] C5.1–C5.4: Frontend Component
- [x] C6.1–C6.2: Test Mocks
- [x] C7.1–C7.4: Validation (parser, Playwright 10/10, pytest 4/4, tsc)
- [x] C8.1–C8.3: Commit

## Validation
- Parser with real HTML: 20 items, valor_total 269.00, key 44 chars, correct CNPJ
- Playwright: 10 passed (4.0s)
- pytest: 4 passed (1.05s)
- TypeScript: tsc --noEmit no errors
- Security: no issues in modified files

## Lessons recorded
- `.contents[1]` is fragile — always prefer `get_text(strip=True)` + regex [EXECUTION]
- Repeated `id="linhaTotal"` is invalid but functional HTML — use `select()` (plural) [EXECUTION]
- BR decimal format requires special handling for "17,9" (no trailing zero) [EXECUTION]
- Key should use `re.sub(r'\s+', '', ...)` instead of `.replace(' ', '')` [EXECUTION]
