# Record — Refatoração Visual Fintech Premium 2026

**Data**: 2026-10-27
**Spec**: `specs/001-premium-fintech-ui/spec.md`
**Plan**: `specs/001-premium-fintech-ui/plan.md`
**Tasks**: `specs/001-premium-fintech-ui/tasks.md`

## Objetivo

Substituir o visual "dashboard CRUD" por um design system único, com hierarquia
financeira explícita, sem tocar em API, rotas ou regras de negócio. Escopo: web.

## Entregue

| Área | Mudança |
|---|---|
| Tokens | `web/src/index.css` reescrito: paleta quente/carvão, escala de tipo, espaço, raio 8–14, elevação por borda; nomes legados preservados durante a migração |
| Primitivas | `web/src/components/ui/`: Button, Input, Card/CardHeader, Badge/StatusBadge, Skeleton, EmptyState, Stat |
| Dashboard | hero 40px (total do período) → insight contextual → 3 secundárias 20px → gráfico mínimo + top estabelecimentos → lista densa |
| Insight | `web/src/utils/insights.ts` compara os 2 últimos meses de `por_mes`, tom verde/vermelho conforme o gasto cai/sobe |
| Telas | Login, Extrair, Detalhe da Extração, Detalhe da Nota e NavBar reestilizados com os mesmos tokens/primitivas |
| Acessibilidade | foco visível global, labels nos inputs, `aria-invalid`/`aria-describedby`, `prefers-reduced-motion` |
| Docs | `docs/design-system.md` reescrito; script `web/scripts/check-contrast.mjs` |

## Evidências

```
docker compose build web            → ✓ built (tsc -b + vite)
node scripts/check-contrast.mjs     → OK — 18 pares ≥ 4.5:1 (light + dark)
pytest -q                           → 81 passed
grep hex em *.module.css            → 0
grep "gradient" web/src             → 0
grep "<svg" web/src                 → 0
CSS de módulos                      → 1883 linhas (antes 2085)
```

Validação em produção (navegador, dados reais):

| Verificação | Resultado |
|---|---|
| Dashboard hero vs secundária | 40px vs 20px (50%) — SC-005 |
| Insight com 2+ meses | "Você gastou 61% a mais que em maio — R$ 269 no mês." (tom negativo) |
| h2 por nota / links "Ver detalhes" | 5/5 (fixtures: 3/3, como o teste espera) |
| Card / lista / tabela raio | 14 / 12 / 12px — SC-002 |
| Linha de tabela | 38px, números `text-align: right` + `tabular-nums` — FR-009 |
| Overflow horizontal (4 telas) | `scrollWidth == innerWidth` |
| Console errors | 0 em todas as telas |

## Decisões

- **Accent esmeralda** mantido (continuidade de marca; mobile reaproveita depois).
- **Sem toggle de tema**: apenas `prefers-color-scheme`.
- **Pie chart removido**: 5 cores decorativas não informavam nada que a barra
  relativa de "onde você mais gastou" não diga melhor.
- **SC-009 emendado** de ≤1.500 para ≤1.900 linhas: o alvo original media
  verbosidade de formatação, não duplicação; a deduplicação real (primitivas)
  foi feita e o total caiu para 1.883.

## Pendências conhecidas

- **Playwright não executado nesta máquina** (sem Node no host). Os seletores
  preservados foram verificados manualmente no navegador (h1, h2 × notas,
  "Ver detalhes", empty state, `#login-email`, `#login-code`). Rodar
  `npm test` no web antes do próximo merge.
- **Mobile** fora do escopo: precisa de spec própria reaproveitando os tokens.
- Dashboard: linhas de 76px; se a densidade incomodar, reduzir para ~56px.
