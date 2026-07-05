# Technical Lessons Learned

<!-- Environment-specific findings, code-level lessons, and constraints. -->

## Cycle 6 — NFC-e Parser Enhancement

### What we learned
- **`.contents[1]` is fragile**: the text node position depends on the BeautifulSoup parser and HTML structure. Always use `get_text(strip=True)` + regex to extract values from spans with nested tags [EXECUTION]
- **Repeated `id="linhaTotal"`**: Invalid but intentional HTML in SEFAZ. `select("#linhaTotal")` returns all; `select_one("#linhaTotal")` returns only the first [EXECUTION]
- **BR decimal format**: Values like "17,9" (no trailing zero) break naive parsers. The double replace (`replace('.', '').replace(',', '.')`) works because the comma only appears as decimal separator [EXECUTION]
- **Key with spaces**: 54 characters vs 44 expected. `re.sub(r'\s+', '', chave.strip())` is more robust than `.replace(' ', '')` [EXECUTION]
- **JSONB + dedicated columns**: The hybrid model (columns for frequently queried fields, JSONB for semi-structured data) is the correct strategy [EXECUTION]
- **Total value from HTML**: More reliable than summation (includes discounts), but requires sum fallback if extraction fails [EXECUTION]
- **`NaN` in HTML**: SEFAZ uses "NaN" for non-applicable change. `br_to_float()` treats it as None [EXECUTION]

### Identified risks
- SSRF via user-supplied URL (`POST /v1/extracoes`) — no domain validation currently [CONSTRAINT]
- Default JWT secret hardcoded in `app/core/config.py` — must be removed before production [CONSTRAINT]
- Parser depends on specific CSS classes from SEFAZ MT (SVRS) — may change without notice [CONSTRAINT]

## Cycle 1 — Security + Import Fixes

### What we learned
- The `database` package was renamed to `abstract` but imports were not updated — 8 broken files [EXECUTION]
- `sa.JSONB` does not exist in SQLAlchemy 2.0+ — use `sa.JSON` [EXECUTION]
- `.env` was always in `.gitignore` and was never committed — good practice from the start [EXECUTION]
- `.env.example` contained `R2_TOKEN` which is not used by `Settings` — removed for clarity [EXECUTION]

### Identified risks
- `abstract.engine` imports `app.core.config` — dependency between sibling packages. If `app.core.config` ever imports something from `abstract`, it forms a circular import [CONSTRAINT]
- NFC-e parser remains fragile (selectors hardcoded for MT) [CONSTRAINT]
- Synchronous extraction in the request (blocks FastAPI) [CONSTRAINT]
- SQLite tests require `schema_translate_map` and `with_variant` for `BigInteger` [CONSTRAINT]

## Cycle 2 — Passwordless Authentication

### What we learned
- SQLite tests require `schema_translate_map` to ignore PostgreSQL schemas (`core`, `raw`, etc.) [EXECUTION]
- `sa.BigInteger` does not auto-increment in SQLite — use `with_variant(sa.Integer(), "sqlite")` [EXECUTION]
- `DateTime(timezone=True)` in SQLite loses timezone — use `expires_at.replace(tzinfo=...)` when comparing [EXECUTION]
- `HTTPBearer` from FastAPI returns 401 (not 403) when token is missing [EXECUTION]
- `get_current_user_id()` now reads from JWT via `Depends(security)` — endpoints are protected by default [EXECUTION]

## Cycle 3 — Frontend MVP

### What we learned
- `react-router` v8 unified the packages: `BrowserRouter`, `Routes`, `Route` now come from `'react-router'` (not `'react-router-dom'`), and there is the subpath `'react-router/dom'` [EXECUTION]
- React 19 ESLint with `react-hooks/use-memo` requires `useCallback`/`useMemo` to have literal arrays as dependencies — does not accept variables [CONSTRAINT]
- React 19 ESLint with `react-hooks/refs` prohibits updating `ref.current` during render (must be in `useEffect`) [CONSTRAINT]
- React 19 ESLint with `react-hooks/set-state-in-effect` prohibits synchronous `setState` in the `useEffect` body [CONSTRAINT]
- Global 401 handler that redirects (`window.location.href`) breaks the login flow if used on auth endpoints — solution: only remove the token and let ProtectedRoute redirect [EXECUTION]
- `pending_email` must be read before removing it from localStorage [EXECUTION]
- `react-router/dom` exports `RouterProvider` and `HydratedRouter` (for SSR/RSC), while declarative components (`BrowserRouter`, `Routes`, `Route`) are in the main package [EXECUTION]

### Pending items
- Replace `LogEmailSender` with real SMTP (Resend, SendGrid, Gmail) [MEMORY]
- Add refresh token + rotation [MEMORY]
- Add Redis for rate limiting in production [MEMORY]
- Migrate `auth_code` table to production SQL in `scripts.sql` [MEMORY]
- Add security headers (CSP) in nginx in production [MEMORY]
- Add custom 404 error page [MEMORY]
