# Implementation Plan: Refatoração Visual — Fintech Premium 2026

**Feature**: `specs/001-premium-fintech-ui/spec.md`
**Branch**: `001-premium-fintech-ui`
**Date**: 2026-10-27

## Summary

Trocar o sistema visual do web por um design system único — tokens, primitivas e
hierarquia — sem tocar em API, rotas ou regras de negócio. A migração é
incremental: os **nomes dos tokens atuais são preservados**, então cada tela pode
ser migrada (e verificada) sem quebrar as outras.

## Technical Context

| Item | Decisão |
|---|---|
| Linguagem | TypeScript, React 19, Vite 8 |
| Estilo | CSS Modules + custom properties (sem framework CSS) |
| Ícones | `lucide-react` (já instalado) |
| Gráficos | Recharts (mantido) |
| Tipografia | Inter (já carregada no `index.html`) |
| Tema | `prefers-color-scheme` (sem toggle nesta versão) |
| Testes | Playwright com `page.route` para mock de API + build gate |
| Alvo | `web/` apenas; mobile fora de escopo |

## Constitution Check

| Princípio | Status |
|---|---|
| I. Spec-first | ✅ spec com critérios SC-001..SC-012 |
| II. Test-first | ⚠️ UI: teste Playwright do insight e do empty state escritos antes da implementação da parte correspondente; CSS validado por asserts de token |
| III. Regressão | ✅ 81 testes backend intocados; build web obrigatório |
| IV. Segurança | ✅ sem novo backend, sem nova dependência, sem segredo |
| V. Deploy | ✅ `docker compose build web` continua a única porta de build |
| VI. Simplicidade | ✅ sem framework novo; primitivas só onde há repetição real |
| VII. Evidência | ✅ comandos de verificação por task |

Sem violações que exijam emenda.

## Design

### 1. Tokens (`web/src/index.css`)

Fonte única. **Nomes atuais mantidos** (`--bg`, `--bg-elevated`, `--text`,
`--accent`, `--border`, `--radius-*`, `--shadow-*`…) e adicionados:

- `--surface`, `--surface-2` (camadas de superfície)
- `--text-secondary`, `--positive`, `--negative`
- escala de espaço (`--space-1..8`), tipos (`--text-xs..2xl`), `--radius-lg: 12px`
- `--elevation-1/2` substituindo sombras pesadas
- `--motion-fast/base`

Paleta: off-white quente (`#FAF9F7`) no claro, carvão (`#0D0F11`) no escuro,
acento esmeralda refinado, verde/vermelho exclusivamente semânticos.

### 2. Primitivas (`web/src/components/ui/`)

`Button`, `Input`, `Card`, `Badge`, `Skeleton`, `EmptyState`, `Stat` + um único
`ui.module.css`. Cada uma resolve estados (hover/focus/disabled/loading) uma vez.

### 3. Telas

| Tela | Mudança |
|---|---|
| Dashboard | hero (total do período) → secundárias → insight → gráfico mínimo → lista densa; skeleton no loading |
| Login | cartão único centralizado, sem sombra pesada, inputs/buttons das primitivas |
| Extrair | formulário compacto, tabela/lista densa com badge de status |
| Detalhe da Extração | progresso e timeline com hierarquia, log em disclosure |
| Detalhe da Nota | tabela densa, números tabulares alinhados à direita, ações discretas |
| NavBar | barra simples, item ativo com indicador, sem ruído |

### 4. Insight contextual

`web/src/utils/insights.ts` — função pura `computeInsight(por_mes)`:

- ordena por ano/mês, compara os dois últimos pontos;
- retorna `{ text, tone }` ou `null` quando há <2 meses ou base zero;
- `tone: "positive"` quando o gasto **cai** (verde), `"negative"` quando sobe.

Sem endpoint novo: usa `por_mes` de `/v1/dashboard/resumo`.

## Ordem de execução

1. Tokens + base (`index.css`) — nada visualmente quebra (nomes preservados).
2. Primitivas `ui/`.
3. NavBar + Dashboard (P1) + teste do insight.
4. Login → Extrair → Detalhe da Extração → Detalhe da Nota (P2/P3).
5. Atualizar `docs/design-system.md`.
6. Gates: build web + Playwright + revisão de tokens.
7. `docs/records/` + commit.

## Verificação (gates da spec)

```bash
docker compose build web                                     # SC-007
grep -rnE "#[0-9a-fA-F]{3,8}" web/src/**/*.module.css        # SC-001 = 0
grep -rn "gradient" web/src                                  # SC-003 = 0
grep -rn "<svg" web/src                                      # SC-010 = 0
wc -l web/src/**/*.module.css                                # SC-009 ≤ 1500
.venv/bin/python -m pytest -q                                # SC-012 = 81
```

Contraste (SC-004): script `web/scripts/check-contrast.mjs` roda no container
`node`, valida os pares texto/fundo dos dois temas e falha abaixo de 4.5:1.

## Riscos

| Risco | Mitigação |
|---|---|
| Quebrar seletor de teste Playwright | textos, `aria-label` e rotas preservados; testes rodam no gate |
| Migração parcial (telas inconsistentes) | tokens com nomes estáveis + ordem por tela + build a cada etapa |
| Charts com cores hardcoded | cores do gráfico vêm de `var(--accent)` / `--border` via getComputedStyle |
| Perda de densidade em telas pequenas | tabela vira lista com `data-label`; testado em 375px |
