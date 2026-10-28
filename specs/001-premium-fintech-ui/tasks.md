# Tasks: Refatoração Visual — Fintech Premium 2026

**Spec**: `specs/001-premium-fintech-ui/spec.md` · **Plan**: `specs/001-premium-fintech-ui/plan.md`

Legenda: `[P]` pode rodar em paralelo · **Verify** = comando/observação que prova a conclusão.

## Fase 1 — Fundação (bloqueia todo o resto)

- [ ] **T001** Reescrever tokens em `web/src/index.css` preservando os nomes atuais e
  adicionando superfície, semânticos, escala de tipo/espaço, elevação e motion.
  **Verify**: `docker compose build web` verde; `grep -c "linear-gradient" web/src/index.css` = 0.
- [ ] **T002** Adicionar script de contraste `web/scripts/check-contrast.mjs` lendo os
  tokens de `index.css` e falhando < 4.5:1.
  **Verify**: rodar no container `node` → "OK (n pares)".
- [ ] **T003** Criar primitivas `components/ui/` (Button, Input, Card, Badge, Skeleton,
  EmptyState, Stat) + `ui.module.css` único.
  **Verify**: `grep -c "#" web/src/components/ui/ui.module.css` = 0 (só tokens).

## Fase 2 — P1: Dashboard

- [ ] **T004** `utils/insights.ts` com `computeInsight` (2 meses, base zero, tom).
  **Verify**: casos cobertos no teste Playwright do T006.
- [ ] **T005** Reescrever `Dashboard.tsx`: hero do total, secundárias subordinadas,
  insight, gráfico mínimo (sem gradiente/sombra), lista densa.
  **Verify**: DOM tem 1 métrica hero; `grep -c "PIE_COLORS"` = 0.
- [ ] **T006** Teste Playwright do insight + empty state com `/v1/dashboard/resumo` mockado.
  **Verify**: `npx playwright test dashboard`.
- [ ] **T007** Skeletons no loading (dashboard) sem salto de layout.
  **Verify**: inspeção + build.

## Fase 3 — P2/P3: telas restantes

- [ ] **T008** [P] `NavBar` — barra simples, item ativo, foco visível. **Verify**: build.
- [ ] **T009** [P] `Login` — cartão único, primitivas, erro em `role="alert"` preservado.
  **Verify**: teste `auth-flow.spec.ts` continua verde.
- [ ] **T010** [P] `Extrair` — form compacto + lista densa + badge de status.
  **Verify**: `nfc-upload.spec.ts` verde.
- [ ] **T011** [P] `ExtracaoDetalhe` — progresso, timeline, log em disclosure.
  **Verify**: `extracao-detalhe-qrcode.spec.ts` verde.
- [ ] **T012** [P] `NotaDetalhe` — tabela densa, números tabulares, ações discretas.
  **Verify**: `dashboard-and-nota-detalhe.spec.ts` verde.
- [ ] **T013** `ErrorMessage`/`LoadingSpinner`/`QrCodeDisplay` alinhados às primitivas.
  **Verify**: `grep` sem hex nesses módulos.

## Fase 4 — Fechamento

- [ ] **T014** Atualizar `docs/design-system.md` (paleta, tipos, primitivas, regras).
- [ ] **T015** Rodar os gates da spec (SC-001, SC-003, SC-007, SC-009, SC-010, SC-012)
  e registrar a saída.
- [ ] **T016** `docs/records/2026-10-27-premium-fintech-ui.md` com evidências.
- [ ] **T017** Commit `feat(web): refactor visual design...` + push.

## Dependências

```
T001 → T002, T003 → (T004..T007) e (T008..T013 em paralelo) → T014..T017
```

T008–T013 são independentes entre si, mas dependem de T001/T003.
