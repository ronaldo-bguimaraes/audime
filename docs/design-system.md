# Design System — Audime

> Fonte da verdade do visual. Implementação: `web/src/index.css` (tokens) e
> `web/src/components/ui/` (primitivas). Nenhum `.module.css` declara cor literal.

## Princípio

**"Calm financial intelligence"** — confiável, preciso, analítico, premium.
Hierarquia antes de decoração: o número que importa domina, o resto apoia.
Inspiração de direção (não de cópia): Linear, Stripe, Revolut, Monzo.

Regras que valem mais que estética:

- Borda + superfície comunicam elevação; sombra é reforço, nunca protagonista.
- Verde e vermelho só significam **movimento financeiro** (entrou/ficou abaixo vs
  saiu/ficou acima). Nunca são cores decorativas.
- Um único acento. O resto é neutro.
- Nada de gradiente, glassmorphism, card flutuante ou sombra pesada.

## Cores

| Token | Light | Dark | Uso |
|---|---|---|---|
| `--bg` | `#faf9f7` (off-white quente) | `#0c0e10` | Fundo da aplicação |
| `--surface` | `#ffffff` | `#14181b` | Cards, tabelas, inputs |
| `--bg-subtle` | `#f3f1ed` | `#1a1f23` | Header de tabela, hover, skeleton |
| `--border` | `#e6e2dc` | `#242a2f` | Divisórias e contornos |
| `--border-strong` | `#d5d0c8` | `#303840` | Contorno de input, botão secundário |
| `--text-h` | `#14161a` | `#f3f5f6` | Títulos e valores |
| `--text` | `#4b4f55` | `#a7aeb5` | Corpo |
| `--text-secondary` | `#5f646b` | `#9aa2aa` | Labels, apoio |
| `--text-muted` | `#6b7076` | `#7c858d` | Metadados |
| `--accent` | `#0a7b5e` | `#34d399` | Ação primária, link, série ativa |
| `--positive` | `#0a7b5e` | `#34d399` | Gasto abaixo do período anterior |
| `--negative` | `#b42318` | `#f97066` | Gasto acima / erro |
| `--warning` | `#a15c00` | `#f5b544` | Aviso (nunca verde/vermelho) |

Contraste mínimo: **4,5:1** texto/fundo e **3:1** UI. Verificação:
`node web/scripts/check-contrast.mjs` (18 pares, light + dark).

## Tipografia

Inter (400/500/600), escala de 6 níveis + micro:

| Token | px | Uso |
|---|---|---|
| `--text-2xl` | 40 | Métrica hero (total do período) |
| `--text-xl` | 28 | Título de tela |
| `--text-lg` | 20 | Valor secundário, título de card |
| `--text-md` | 16 | Subtítulo |
| `--text-base` | 14 | Corpo, tabela, valor de linha |
| `--text-sm` | 13 | Apoio, botão, link |
| `--text-xs` | 12 | Label, metadado |
| `--text-2xs` | 11 | Badge, header de tabela |

Números são **sempre tabulares** (`font-variant-numeric: tabular-nums`, aplicado
globalmente) e alinhados à direita em tabelas. Títulos com `letter-spacing`
negativo; nunca justificar texto.

## Espaço, raio, elevação

- Espaço: `--space-1..8` (4, 8, 12, 16, 20, 24, 32, 48).
- Raio: `--radius-sm 8` · `--radius-md 10` · `--radius-lg 12` · `--radius-xl 14`.
  Card usa 14; input/botão 10; badge 8.
- Elevação: `--elevation-1` (1px) e `--elevation-2`. Cards usam **borda**, não sombra.
- Movimento: 120ms (micro) e 180ms (transição), com `prefers-reduced-motion`.

## Primitivas (`web/src/components/ui/`)

| Componente | Variantes |
|---|---|
| `Button` | `primary`, `secondary`, `ghost`, `danger` · `sm`, `md` |
| `Input` | label + hint/erro, `aria-invalid`, `aria-describedby` |
| `Card` / `CardHeader` | com/sem padding, header com ações |
| `Badge` / `StatusBadge` | `neutral`, `positive`, `negative`, `warning`, `progress` |
| `Skeleton` | placeholder com pulse discreto |
| `EmptyState` | ícone + título + descrição + ação |
| `Stat` | label/valor/hint, `hero` para a métrica principal |

Regra: se um botão/input/badge aparece em duas telas, ele é primitiva — não uma
classe nova no módulo da página.

## Hierarquia do dashboard

1. **Hero**: total do período, 40px, primeiro no fluxo.
2. **Insight**: uma frase comparando com o mês anterior (cor semântica).
3. **Secundárias**: 3 métricas em 20px — nunca competem com o hero.
4. **Apoio**: gráfico de barras mensal (sem eixo Y, sem grid vertical, sem
   gradiente) + top estabelecimentos com barra relativa.
5. **Lista**: uma linha por nota, valor à direita, ação "Ver detalhes".

## Tabelas e estados

- Linha de tabela: 36–44px, header em `--text-2xs` maiúsculo, hover sutil.
- Abaixo de 720px a tabela vira lista com `data-label` (sem scroll horizontal).
- Loading: skeleton com a mesma geometria do conteúdo (sem salto de layout).
- Vazio: frase + próxima ação, nunca ilustração decorativa.
- Erro: mensagem + "Tentar novamente" no mesmo padrão visual.
- Foco: `outline: 2px solid var(--accent)` visível em todo interativo.

## Verificação

```bash
node web/scripts/check-contrast.mjs                      # contraste WCAG
grep -rnE "#[0-9a-fA-F]{3,8}" web/src --include="*.module.css"   # deve ser 0
grep -rn "gradient" web/src                              # deve ser 0
grep -rn "<svg" web/src                                  # deve ser 0 (lucide)
docker compose build web                                 # tsc + vite
```
