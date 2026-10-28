# Sprint Record — Issue #20: Leitura de QR Code via câmera na tela de Nova Extração

**Date**: 2026-07-05
**Sprint Type**: Incremental Feature
**Product Owner Review**: ✅ Complete

---

## Issue Reference

[#20](https://github.com/ronaldo-bguimaraes/audime/issues/20) — Leitura de QR Code via câmera na tela de Nova Extração

---

## What Was Delivered

A camera button with a QR Code scanner modal on the **Nova Extração** page (`Extrair.tsx`). Users can now click a 📷 button next to the URL input to open a live camera feed, scan a QR Code, and have the URL filled automatically.

### New Hook

- **`web/src/hooks/useQrCodeScanner.ts`** — React hook that manages the QR Code scanner lifecycle using `qr-scanner`:
  - `startScanning()` — initializes camera via `getUserMedia` and starts QR decoding
  - `stopScanning()` — stops camera stream, destroys scanner, removes test seam
  - Tracks `status` (idle | scanning | error) and `errorMessage`
  - Handles all DOMException types (`NotAllowedError`, `NotFoundError`, `NotReadableError`, `AbortError`) with Portuguese messages
  - Exposes `window.__injectQrResult` test seam for Playwright testing
  - Validates scanned URLs with regex `/^https?:\/\//` — non-http content is ignored

### New Component

- **`web/src/components/QrCodeScanner.tsx`** — Modal component with:
  - `role="dialog"`, `aria-modal="true"` for accessibility
  - `<video autoPlay playsInline muted>` for camera feed
  - Cancel button to close modal and stop camera
  - Error state with `role="alert"` when camera is unavailable
  - Close (×) button in modal header

### Integration

- **`Extrair.tsx`** — Modified:
  - Camera 📷 button with `aria-label="Escanear QR Code"` inside an `.inputRow` flex container
  - `<QrCodeScanner>` component rendered conditionally based on `scannerOpen` state
  - `handleQrScan` callback fills URL and closes modal on successful scan

- **`Extrair.module.css`** — New CSS classes:
  - `.inputRow` — flex layout for input + camera button
  - `.cameraButton` — styled 42×42px icon button
  - `.videoContainer` — 4:3 aspect ratio, black background, rounded
  - `.video` — cover-fit video
  - `.cameraError` — red alert box for camera errors
  - `.modalActions` + `.cancelButton` — centered cancel button

### Test Infrastructure

- **`web/tests/extracao-qrcode-camera.spec.ts`** — New Playwright test file with 6 tests:
  - CAM-002: Camera button visible
  - CAM-003: Modal opens with `<video>` element
  - CAM-004: Cancel closes modal and stops camera
  - CAM-005: Valid HTTP QR Code fills input and closes modal
  - CAM-006: Non-HTTP QR Code is ignored, scanner continues
  - CAM-007: Camera unavailable shows friendly error

### Dependencies

- `qr-scanner` v1.4.2 — QR Code scanning library (by Nimiq), chosen over `jsqr` (abandoned) and `html5-qrcode` (440+ issues, 2.63 MB bundle)

---

## Files Changed/Created

| File | Action |
|------|--------|
| `web/package.json` | Added `qr-scanner` dependency |
| `web/package-lock.json` | Auto-updated |
| `web/src/hooks/useQrCodeScanner.ts` | **Created** — Scanner lifecycle hook |
| `web/src/components/QrCodeScanner.tsx` | **Created** — Camera modal component |
| `web/src/pages/Extrair.tsx` | Modified — added camera button + modal integration |
| `web/src/pages/Extrair.module.css` | Modified — added scanner-related styles |
| `web/tests/extracao-qrcode-camera.spec.ts` | **Created** — 6 Playwright tests |

---

## Test Results Summary

```
22 tests total
  ✅ 17 passed (11 existing + 6 new camera tests)
  ❌ 5 failed (pre-existing failures, unrelated)
```

### Camera Tests (all ✅ passed)

| Test | Status | Notes |
|------|--------|-------|
| CAM-002: Camera button visible | ✅ PASS | Button with `aria-label="Escanear QR Code"` found |
| CAM-003: Modal opens with video | ✅ PASS | `role="dialog"` + `<video autoplay playsinline>` visible |
| CAM-004: Cancel closes modal | ✅ PASS | Modal hidden after cancel; `getUserMedia` was called |
| CAM-005: Valid QR fills input | ✅ PASS | `__injectQrResult` with http URL fills `#extracao-url` |
| CAM-006: Non-http QR ignored | ✅ PASS | "Hello World" ignored, modal stays open, then http works |
| CAM-007: Camera error handled | ✅ PASS | `getUserMedia` rejection → `role="alert"` with PT message |

### TypeScript

- `npx tsc --noEmit` — **exit code 0** (no errors)

### Regression Check

- All 6 new tests pass. The 5 pre-existing failures (`auth-flow.spec.ts`, `dashboard-and-nota-detalhe.spec.ts`) remain unchanged — **zero regression**.

---

## Decisions Made

| Decision | Choice | Reason |
|----------|--------|--------|
| QR scanning library | `qr-scanner` (Nimiq) | Active maintenance, Web Worker decoding, 59 kB, built-in camera management, TypeScript types. Chosen over `jsqr` (5y inactive) and `html5-qrcode` (440+ issues, 2.63 MB) |
| Architecture | Component + Hook (`QrCodeScanner` + `useQrCodeScanner`) | Separation of concerns; hook is testable; component handles UI only |
| Test strategy | `addInitScript` mock for getUserMedia + `__injectQrResult` test seam | No real camera needed; deterministic QR injection |
| Error handling | Switch on DOMException name | Covers all `getUserMedia` error types with Portuguese messages |
| Camera facing | `environment` (traseira) | Correct for QR Code scanning on mobile |
| Video attrs | `autoPlay`, `playsInline`, `muted` | Required for iOS Safari compatibility |
| URL validation | Regex `/^https?:\/\//` | Prevents XSS via non-http QR payloads (e.g. `javascript:`) |

---

## Acceptance Criteria Verification

All 12 acceptance criteria verified:

| Criterion | Status | Evidence |
|-----------|--------|----------|
| CAM-001 | ✅ | `qr-scanner@^1.4.2` in `package.json` |
| CAM-002 | ✅ | Test passed — button with camera icon visible |
| CAM-003 | ✅ | Test passed — modal with `<video>` opens |
| CAM-004 | ✅ | Test passed — cancel closes modal, camera stopped |
| CAM-005 | ✅ | Test passed — http QR fills input and closes modal |
| CAM-006 | ✅ | Test passed — non-http ignored, scanner continues |
| CAM-007 | ✅ | Test passed — error message in Portuguese shown |
| CAM-008 | ✅ | Same flow as CAM-007 (NotAllowedError handled) |
| CAM-009 | ✅ | 7 new CSS classes in `Extrair.module.css` |
| CAM-010 | ✅ | `tsc --noEmit` exit code 0 |
| CAM-011 | ✅ | No regression — 5 pre-existing failures unchanged |
| CAM-012 | ✅ | `addInitScript` + `__injectQrResult` mock works |

---

## Known Issues / Limitations

1. **iOS Safari PWA** — Camera permission may not persist in "Add to Home Screen" PWAs (WebKit bug #215884). User should open Safari directly.
2. **HTTPS required** — `getUserMedia` only works in secure contexts (HTTPS). `localhost` is exempt for development.
3. **No camera selection** — Uses default camera (environment-facing when available). No front/back switch UI.
4. **No timeout** — Scanner runs indefinitely until QR detected or user cancels. Future enhancement could add a timeout with a friendly message.
5. **Pre-existing test failures** — 5 tests fail due to unrelated dashboard rendering issues (not caused by this sprint).

---

## Security Audit Summary

| Category | Result |
|----------|--------|
| Credential leak scan | ✅ None found |
| Dependency vulnerabilities | ✅ 0 CVEs (`qr-scanner`, `qrcode`) |
| Privacy (getUserMedia) | ✅ Triggered by user click only |
| Resource cleanup | ✅ Stream stopped on modal close |
| XSS prevention | ✅ URL validated with regex; no innerHTML |

---

## Lessons Added

Learnings from this cycle:
- `qr-scanner` library integration with React (constructor + start/stop/destroy lifecycle)
- Playwright `addInitScript` for mocking `navigator.mediaDevices.getUserMedia` with canvas `captureStream`
- Test seam pattern (`window.__injectQrResult`) for injecting QR decode results in Playwright tests
- Handling all DOMException types from `getUserMedia` with user-friendly messages
- `playsInline` + `muted` video attributes are mandatory for iOS Safari camera playback
