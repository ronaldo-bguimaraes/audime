# Sprint Record — Issue #19: Substituir URL por QR Code na tela de Detalhes da Extração

**Date**: 2026-07-05
**Sprint Type**: Incremental Feature
**Product Owner Review**: ✅ Complete

---

## Issue Reference

[#19](https://github.com/ronaldo/audime/issues/19) — Substituir URL por QR Code na tela de Detalhes da Extração

---

## What Was Delivered

The raw URL text displayed in the "Extração Detalhe" page was replaced with a scannable QR Code image generated from that URL. Two action buttons ("Abrir" and "Copiar") were added alongside the QR Code.

### New Component

- **`web/src/components/QrCodeDisplay.tsx`** — A self-contained React component that:
  - Generates a QR Code from a URL using the `qrcode` library's `toDataURL()` method (180×180px PNG)
  - Renders a fallback (`"—"`) when the URL is null/undefined
  - Shows a loading placeholder while the QR Code is being generated
  - Provides an "Abrir" link (`<a target="_blank" rel="noopener noreferrer">`) to open the URL in a new tab
  - Provides a "Copiar" button that copies the URL to clipboard with a fallback mechanism

- **`web/src/components/QrCodeDisplay.module.css`** — Scoped CSS Module with styles for:
  - `.qrContainer` — flex column, centered layout
  - `.qrImage` — 180×180px display
  - `.qrPlaceholder` — animated pulse for loading state
  - `.actionRow` — horizontal button layout
  - `.actionButton` — styled buttons/links with hover and focus states
  - `.fallback` — secondary text style
  - `.srOnly` — screen-reader-only status message

### Integration

- **`ExtracaoDetalhe.tsx`** — The URL infoRow was updated to render `<QrCodeDisplay url={data.url} />` instead of the raw URL `<span>`.

### Test Infrastructure

- **`web/tests/fixtures.ts`** — Updated with:
  - `mockExtracao` (id 1, with valid `url`)
  - `mockExtracaoSemUrl` (id 2, `url: null`)
  - Method-differentiated route handler for `**/v1/extracoes*` (GET returns array, POST handles upload)
  - Individual route `**/v1/extracoes/*` returns `mockExtracao`

- **`web/tests/extracao-detalhe-qrcode.spec.ts`** — New Playwright test file with 6 tests covering:
  - CAT-QR-002: QR Code displayed when URL present
  - CAT-QR-003: QR Code absent with fallback when URL null
  - CAT-QR-004: "Abrir" opens URL in new tab
  - CAT-QR-005: "Copiar" copies to clipboard
  - CAT-QR-006: No buttons when URL null
  - CAT-QR-011: "Abrir" has `rel="noopener noreferrer"`

---

## Files Changed/Created

| File | Action |
|------|--------|
| `web/package.json` | Added `qrcode` and `@types/qrcode` dependencies |
| `web/src/components/QrCodeDisplay.tsx` | **Created** — QR Code component |
| `web/src/components/QrCodeDisplay.module.css` | **Created** — Component styles |
| `web/src/pages/ExtracaoDetalhe.tsx` | Modified — replaced URL `<span>` with `<QrCodeDisplay>` |
| `web/src/pages/ExtracaoDetalhe.module.css` | Modified (if needed — verify) |
| `web/tests/fixtures.ts` | Modified — added mock extractions URL/GET handler |
| `web/tests/extracao-detalhe-qrcode.spec.ts` | **Created** — Playwright tests |

---

## Test Results Summary

```
16 tests total
  ✅ 11 passed
  ❌ 5 failed (pre-existing failures in auth-flow.spec.ts and dashboard-and-nota-detalhe.spec.ts)
```

### QR Code Tests (all ✅ passed)

| Test | Status | Notes |
|------|--------|-------|
| CAT-QR-002: QR displayed when URL present | ✅ PASS | `<img>` with `data:image/` src visible, raw URL not visible |
| CAT-QR-003: QR absent when URL null | ✅ PASS | No `<img>`, fallback "—" visible |
| CAT-QR-004: "Abrir" opens new tab | ✅ PASS | New page event URL matches extraction URL |
| CAT-QR-005: "Copiar" copies to clipboard | ✅ PASS | Clipboard readback matches URL |
| CAT-QR-006: No buttons when URL null | ✅ PASS | Neither "Abrir" nor "Copiar" present |
| CAT-QR-011: `rel="noopener noreferrer"` | ✅ PASS | `rel` attribute contains both values |

### Pre-existing Failures (unrelated to this sprint)

| Test | File | Issue |
|------|------|-------|
| Login flow with valid credentials | `auth-flow.spec.ts` | `h1` "Notas Fiscais" not found after login |
| Dashboard shows list of notes | `dashboard-and-nota-detalhe.spec.ts` | `a:has-text("Ver detalhes")` count 0 |
| Dashboard navigation to note details | `dashboard-and-nota-detalhe.spec.ts` | Timeout — link not found |
| Note detail shows items correctly | `dashboard-and-nota-detalhe.spec.ts` | `h1` with empresa name not found |
| Responsive behavior on mobile | `dashboard-and-nota-detalhe.spec.ts` | `a:has-text("Ver detalhes")` count 0 |

### TypeScript

- `npx tsc --noEmit` — **exit code 0** (no errors)

---

## Decisions Made

| Decision | Choice | Reason |
|----------|--------|--------|
| QR library | `qrcode` (npm) + `@types/qrcode` | Mature, well-typed, simple `toDataURL()` API; no React-specific wrapper needed |
| Component architecture | Standalone `QrCodeDisplay` component | Separates concerns from `ExtracaoDetalhe`; easily testable; reusable |
| "Abrir" implementation | `<a href={url} target="_blank" rel="noopener noreferrer">` | Uses native browser behavior; no JS handler needed; `rel` prevents tab-napping |
| Clipboard approach | `navigator.clipboard.writeText` with `execCommand` fallback | Standard pattern; covers both secure (HTTPS) and non-secure contexts |
| CSS approach | CSS Module (`QrCodeDisplay.module.css`) | Consistent with existing codebase pattern; scoped by default |
| Mock fixture design | Method-differentiated route handler | Allows existing upload POST mock to coexist with new GET mock |
| Dual mock extractions | One with URL, one with `url: null` | Enables testing both happy path and null-fallback without changing fixture data between tests |
| QR Code size | 180×180px | Readable at typical mobile scan distance; matches standard QR Code sizing recommendations |

---

## Acceptance Criteria Verification

All 12 acceptance criteria verified:

| Criterion | Status | Evidence |
|-----------|--------|----------|
| CAT-QR-001 | ✅ | `qrcode` in `package.json` deps |
| CAT-QR-002 | ✅ | Test passed — QR `<img>` visible, URL text hidden |
| CAT-QR-003 | ✅ | Test passed — no QR, fallback "—" when URL null |
| CAT-QR-004 | ✅ | Test passed — new tab opens with correct URL |
| CAT-QR-005 | ✅ | Test passed — clipboard contains URL |
| CAT-QR-006 | ✅ | Test passed — no buttons when URL null |
| CAT-QR-007 | ✅ | Fixtures updated with mock URL extraction |
| CAT-QR-008 | ✅ | CSS Module has all required classes |
| CAT-QR-009 | ✅ | `tsc --noEmit` exit code 0 |
| CAT-QR-010 | ✅ | No regression — 5 pre-existing failures unchanged |
| CAT-QR-011 | ✅ | Test passed — `rel="noopener noreferrer"` present |
| CAT-QR-012 | ✅ | Code review — `execCommand` fallback implemented |

---

## Known Issues / Limitations

1. **QR Code is generated client-side only** — No server-side QR generation; requires JavaScript to be enabled
2. **No QR Code download button** — Listed as out of scope; user cannot save the QR image directly
3. **No custom QR styling** — Uses default black-on-white; no logo overlay or color customization
4. **Pre-existing test failures** — 5 tests in `auth-flow.spec.ts` and `dashboard-and-nota-detalhe.spec.ts` fail due to unrelated issues (dashboard rendering, navigation). These existed before this sprint and are not caused by the QR Code changes.
5. **"Copiar" visual feedback** — Button text changes to "Copiado!" for 2 seconds, but only the button text changes (no toast/notification). This is sufficient for MVP.

---

## Lessons Added

Learnings from this cycle recorded in `.agents/state/lessons.md` (Cycle 8 section):
- `qrcode` npm package workflow with React
- Playwright `waitForEvent("page")` for testing `target="_blank"`
- Clipboard permissions in Playwright (`grantPermissions`)
- Clipboard fallback pattern
- Pre-existing test failures don't block feature delivery
