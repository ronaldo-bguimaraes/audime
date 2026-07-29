# Lessons Learned

<!-- Accumulated across cycles. Every failure becomes a lesson here. -->

## Cycle 10 — Sprint All 11 Issues (Fase 1-3)

### What worked
- **Phased approach (P0 → P1 → P2)** kept the sprint manageable: bugs first, enhancements second, features third
- **Real HTML fixtures** resolved 10 xfails in one shot — simplified fixtures were the root cause of false negatives
- **Force-reset endpoint** is a simple but effective escape hatch for stuck extractions without manual DB intervention
- **Recharts** proved to be a good choice for React charting — lightweight, declarative, works well with TypeScript

### What we learned
- **SQLite test state pollution**: Running `pytest` multiple times without cleaning `test.db` causes cascading failures. Always clean the database between test runs for accurate metrics. [EXECUTION]
- **Parser edge cases**: Empty HTML, malformed HTML, missing item tables — each reveals a different parsing vulnerability. Edge case tests are essential for parser robustness. [EXECUTION]
- **Playwright without backend**: 7/8 Playwright failures are `ECONNREFUSED` because the backend isn't running. Frontend-only tests need proper mocking or a running backend. [CONSTRAINT]
- **Semantic debate: 0 vs None**: When a data element doesn't exist (no item table), should the parser return `0` (assume zero) or `None` (unknown)? This is a design decision that should be explicit in the spec. [DESIGN]
- **81 tests from 54**: Adding 27 new tests (+50%) without breaking any existing ones is feasible when tests are well-isolated and follow the same patterns. [PROCESS]

### What didn't work
- **Attempting 11 issues in one sprint**: 2 of 11 issues (#3 Google OAuth, #5 Fluxo Extração) were not started. The scope was too large for a single sprint cycle.
- **Playwright CI dependency**: Without a running backend, most Playwright tests fail. Need to either mock API calls or provide docker-compose for CI.

## Cycle 9 — Leitura de QR Code via câmera na tela de Nova Extração (#20)

### What worked
- **Component + Hook separation** (`QrCodeScanner` + `useQrCodeScanner`) kept the logic testable and the UI clean. The hook manages all scanner state while the component only handles rendering.
- **`qr-scanner` library** was the right choice — built-in camera management, Web Worker decoding, TypeScript types, and a simple constructor-based API.
- **Test seam pattern** (`window.__injectQrResult`) made QR decode testing deterministic without needing real camera hardware or QR code images.
- **Canvas `captureStream` mock** for `getUserMedia` worked reliably in Playwright — no flaky test issues.

### What we learned
- **`qr-scanner` lifecycle**: `new QrScanner(video, onDecode, options)` → `scanner.start()` → `scanner.stop()` → `scanner.destroy()`. The `destroy()` call is critical to release camera resources. [EXECUTION]
- **`playsInline` + `muted` are mandatory** on the `<video>` element for iOS Safari camera playback. Without these, the video feed stays black on iOS. [CONSTRAINT]
- **`getUserMedia` DOMException handling**: Each error type (`NotAllowedError`, `NotFoundError`, `NotReadableError`, `AbortError`, `OverconstrainedError`) has a distinct cause and needs a specific user-friendly message. [EXECUTION]
- **`page.addInitScript` runs before navigation** — it must be called before `page.goto()` to mock `navigator.mediaDevices.getUserMedia` effectively. [EXECUTION]
- **`OverconstrainedError` fallback**: If `facingMode: "environment"` fails (device has no rear camera), fall back to `{ video: true }` without constraints. [CONSTRAINT]
- **`qr-scanner` vs alternatives**: `jsqr` is abandoned (5 years without updates) and requires manual camera management. `html5-qrcode` has 440+ open issues and a 2.63 MB bundle. `qr-scanner` is the best maintained and most performant option. [DECISION]

## Cycle 8 — Substituir URL por QR Code na tela de Detalhes da Extração (#19)

### What worked
- **Dedicated component (`QrCodeDisplay`)** kept the component clean and testable — separation from `ExtracaoDetalhe.tsx` made the Playwright tests simpler (just query the URL row)
- **CSS Module in a separate file** (`QrCodeDisplay.module.css`) kept styles scoped and reusable
- **Method-differentiated route handler** in the mock fixture (`GET` vs `POST` for `**/v1/extracoes*`) allowed existing upload mocks to coexist with the new QR Code mocks
- **Dual mock extractions** (one with URL, one with `url: null`) made it easy to test both the "happy path" and the null-fallback path

### What we learned
- **The `qrcode` NPM package works well with React**: `QRCode.toDataURL(url, { width, margin })` returns a base64 PNG data URL that can be set directly as an `<img>` `src`. The `@types/qrcode` package provides TypeScript types. [EXECUTION]
- **Playwright's `context().waitForEvent("page")` is the correct way to test `target="_blank"` navigation**: clicking an `<a target="_blank">` opens a new page in the browser context; waiting for the "page" event and asserting `newPage.url()` verifies the link works. [EXECUTION]
- **`navigator.clipboard` requires permissions in Playwright**: `context.grantPermissions(["clipboard-read", "clipboard-write"])` must be called before the test. This is only needed for the clipboard test, so it's scoped to that single test. [EXECUTION]
- **The clipboard fallback pattern** (try `navigator.clipboard.writeText`, fall back to `document.execCommand('copy')` with a temp `<textarea>`) remains the standard approach for non-HTTPS contexts. [CONSTRAINT]
- **Pre-existing test failures don't block new features**: The 5 failing tests in `auth-flow.spec.ts` and `dashboard-and-nota-detalhe.spec.ts` are unrelated to QR Code changes and have been failing since earlier cycles. [PROCESS]

## Cycle 7 — Fix Dashboard Empty (Transform Pipeline & Raw Fallback)

### Discovery
- **Product manager + tech_lead in parallel is efficient**: both confirmed the same root cause from different angles (user experience vs. architecture) [PROCESS]
- The MG parser test fixture is **completely different** from what the parser expects — not a parser bug, but a test data issue [EXECUTION]

### What we learned
- **`_queue_name` must match in chained ARQ jobs**: When worker A enqueues worker B, both `enqueue_job` calls must specify `_queue_name` matching the `WorkerSettings.queue_name`. Omitting it sends the job to ARQ's default queue (`arq:queue`) which no worker polls. [EXECUTION]
- **Dashboard list endpoint needed raw fallback**: The individual nota endpoint had `_build_from_raw()` fallback but the list endpoint didn't. This pattern (list has no fallback, detail has fallback) is an easy oversight. [EXECUTION]
- **Test fixtures with simplified HTML are dangerous**: A simplified fixture that doesn't match real HTML structure leads to false confidence — tests pass trivially (empty items list makes assertions vacuously true) or fail mysteriously. Fixtures should mirror real HTML. [CONSTRAINT]
- **`transformar_extracao` is URL-independent**: The function only needs `id_extracao` to find raw data. This makes it suitable for backfill and transform-only reprocess modes. [EXECUTION]
- **xfail markers document known issues**: Marking broken MG parser tests as xfail with a clear reason allows the suite to pass reliably while documenting the gap. [EXECUTION]
- **File-based SQLite tests are fragile**: `sqlite:///./test.db` leaves stale state between runs. `:memory:` would be more robust. [CONSTRAINT]

### What worked
- Parallel discovery with product_manager (user-facing) + tech_lead (architecture) identified the complete root cause set
- TDD approach: tests failed first (proving the bug), then implementation made them pass
- Specification focused on the user's actual problem ("nenhuma nota visivel") kept scope bounded
- Both validation agents (qa_engineer + devops_engineer) passed on first attempt

## Cycle 6 — NFC-e Parser Enhancement

### What worked
- The questionador correctly identified that `.contents[1]` was fragile (HIGH severity) — replacement with `get_text(strip=True)` + regex solved the problem
- The explicador confirmed that the hybrid approach (dedicated columns + JSONB) is recommended by PostgreSQL literature
- The parser tested with real HTML validated all 33 criteria at once
- `br_to_float()` with double replace (`.` → ``, `,` → `.`) works for all real HTML cases

## Cycle 1 — Security + Import Fixes

### What worked
- Historical scan with `git log -p | grep` is sufficient for small projects — no need for gitleaks/trufflehog
- `rg` is effective for finding residual references after package rename
- `pydantic-settings` with `extra="ignore"` avoids failures from extra vars in `.env`

## Cycle 2 — Passwordless Authentication

### What worked
- Abstract `EmailSender` with `LogEmailSender` allows swapping implementations without touching the flow
- `PyJWT` with HS256 is simple and direct for MVP
- Basic rate limiting with `AuthCode.attempts` + 60s cooldown

## Cycle 3 — Frontend MVP

### What worked
- Spec-first with 52 verifiable criteria precisely guided the implementation
- CSS Modules (Vite native) — zero setup, component scoping, no dependencies
- Native fetch with wrapper in `api/client.ts` — simple and sufficient for 4 endpoints
- AuthProvider with Context API — eliminated token prop drilling
- `Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" })` for BRL formatting
- Vite proxy (`server.proxy`) for routing `/v1` to backend in dev
- 60s resend countdown with `setInterval` + `clearInterval`

## Cycle 5 — Subagent Aprendiz Creation

### What worked
- Parallel research with questionador + explicador revealed issues the spec did not anticipate (Analysis Mode is read-only, path-based permissions have bugs)
- Spec-first + research + adjustment worked: the final design is better than the initial

### What we learned
- The Loopback Analysis Mode is **read-only by definition** — agents that write (like the aprendiz) should not be listed there [ROUTING]
- The aprendiz combines research + questioning + explanation + recording, but it is the **only research agent with write permission** — this clearly differentiates it from questionador and explicador [CORE]
- The subagent list format uses **bold** in `.agents/agents/loopback.md` and **backticks** in `.opencode/agents/loopback.md` — different styles but consistent with each file's context [MEMORY]
- The initial spec may contain incorrect assumptions that research corrects — the questioning cycle is essential [CORE]

## Cycle 4 — Skills vs Agents

### What we learned
- The decisive criterion between skill and agent **is not scope**, but **need for context isolation**: skills inherit the calling agent's context, agents have their own isolated context [CORE]
- Skills are ideal for **additive** tasks (research, questioning) that benefit from rich context — not for **critical** tasks (validation, auditing) that require independence [ROUTING]
- Parallelism (`task()` for multiple simultaneous subagents) is a concrete advantage of agents that skills cannot replicate — skills are text blocks injected sequentially [CONSTRAINT]
- The maker-checker split is the most important architectural principle of the loopback cycle: **proposer ≠ approver** — and this requires context isolation that only agents provide (with `context: fork` or fresh context) [CORE]
- Research subagents (questionador, explicador) could be unified into a `pesquisador` skill without functional loss, only with loss of parallelism — an acceptable tradeoff if simplicity is a priority [ROUTING]
- Skills 2.0 (issue #17791 with `context: fork`, `allowed_tools`) could completely change this analysis — monitor for reassessment [MEMORY]
- The agent → skill migration is costly (opencode.json, definition files, AGENTS.md, loopback.md) — only worth it if the gain is clear and measurable [EXECUTION]
