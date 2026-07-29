# Design System — Audime

> Fonte da verdade para estilo visual, cores, tipografia, componentes e decisões de design.

---

## 1. Propósito

Audime é um app de gestão financeira pessoal com foco em **economia e positividade**. O design deve passar sensação de:
- **Confiança** — dados financeiros precisam soar sólidos
- **Leveza** — finanças pessoais não devem ser intimidadoras
- **Progresso** — cada interação reforça "você está no controle"

---

## 2. Paleta de Cores

### 2.1 Brand (Verde Esmeralda)

| Token | Light | Dark | Uso |
|-------|-------|------|-----|
| `--accent` | `#059669` | `#34d399` | Botões primários, links, indicadores ativos |
| `--accent-hover` | `#047857` | `#6ee7b7` | Hover de elementos accent |
| `--accent-light` | `rgba(5, 150, 105, 0.1)` | `rgba(52, 211, 153, 0.12)` | Backgrounds sutis, badges positivos |
| `--accent-border` | `rgba(5, 150, 105, 0.3)` | `rgba(52, 211, 153, 0.3)` | Bordas de foco, outlines |

**Por que verde?** Associação universal com crescimento, dinheiro, saúde financeira. Tom esmeralda (não verde limão) passa maturidade.

### 2.2 Highlight (Âmbar)

| Token | Light | Dark | Uso |
|-------|-------|------|-----|
| `--highlight` | `#f59e0b` | `#fbbf24` | Selos de economia, alerts positivos, ícones de meta |
| `--highlight-light` | `#fef3c7` | `#422006` | Background de badges de meta/destaque |

**Por que âmbar?** Acentua sem competir com o verde. Usado para "atenção positiva" — você está no caminho certo.

### 2.3 Neutros

| Token | Light | Dark | Uso |
|-------|-------|------|-----|
| `--bg` | `#f8fafc` | `#0f172a` | Fundo geral (slate muito suave) |
| `--bg-elevated` | `#ffffff` | `#1e293b` | Cards, modais, superfícies elevadas |
| `--bg-subtle` | `#f1f5f9` | `#1e293b` | Hover de linhas, inputs |
| `--border` | `#e2e8f0` | `#334155` | Bordas padrão |
| `--border-strong` | `#cbd5e1` | `#475569` | Bordas de destaque |

**Por que slate (cinza azulado) em vez de gray/cool-gray?** O tom azulado sutíl reforça a sensação de confiança e profissionalismo (bancos usam neutros azulados). Evita o amarelado de "paper envelhecido".

### 2.4 Texto

| Token | Light | Dark | Uso |
|-------|-------|------|-----|
| `--text` | `#475569` | `#94a3b8` | Corpo de texto |
| `--text-h` | `#0f172a` | `#f1f5f9` | Títulos, valores em destaque |
| `--text-muted` | `#94a3b8` | `#64748b` | Labels, hints, metadados |

### 2.5 Semântica

| Token | Light | Dark | Uso |
|-------|-------|------|-----|
| `--success` (+ bg/border) | verde (`#16a34a`) | verde escuro | Operações concluídas |
| `--error` (+ bg/border) | vermelho (`#dc2626`) | vermelho escuro | Erros, falhas |
| `--warning` (+ bg/border) | âmbar (`#d97706`) | âmbar escuro | Alertas |
| `--info` (+ bg/border) | azul (`#2563eb`) | azul escuro | Informações neutras |

---

## 3. Tipografia

### 3.1 Família

**Inter** (Google Fonts) — única fonte do sistema.

```css
--font-sans: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
--font-mono: "SF Mono", ui-monospace, Consolas, monospace;
```

**Por que Inter?** Designed para telas, ótima legibilidade em pesos leves, suporte a `font-feature-settings` para números tabulares (essencial para valores financeiros).

### 3.2 Escala

| Nível | Tamanho | Peso | Uso |
|-------|---------|------|-----|
| Hero | `28px` | `700` | Saldo principal, totais grandes |
| Título página | `22px` | `600` | Cabeçalhos de página |
| Título card | `16px` | `600` | Títulos dentro de cards |
| Corpo | `14px` | `400` | Texto geral |
| Label | `12px` | `500` | Rótulos de campo, badges |
| Valor | `14px` | `700` | Valores monetários em lista |
| Valor grande | `22px` | `700` | Valores em cards de resumo |
| Moeda | `12px` | `500` | Prefixo "R$" antes de valores |

### 3.3 Números

Sempre usar `font-feature-settings: "tnum"` para números tabulares (mesma largura) em valores financeiros:

```css
font-feature-settings: "cv02", "cv03", "cv04", "cv11", "tnum";
```

Isso impede que números "pulem" visualmente ao mudar de `1.234,00` para `8.765,43`.

### 3.4 Formatação monetária

- Sempre `Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" })` ou `formatBRL()`
- Prefixo `R$` junto do valor, sem espaço extra
- Centavos sempre visíveis (ex: `R$ 42,00`, não `R$ 42`)

---

## 4. Espaçamento e Layout

### 4.1 Grid

- Layout usa padding lateral de `24px` (desktop) → `16px` (mobile)
- Gaps padrão: `8px` (interno), `12px` (entre cards), `20px` (entre seções)
- Breakpoint mobile: `700px`

### 4.2 Cards

- Border radius: `12px` (`--radius-lg`)
- Sombra: `--shadow-sm` (light) / `--shadow-md` (dark)
- Padding interno: `16px`
- Hover: `translateY(-1px)` + sombra mais alta (transição `200ms ease-out`)

### 4.3 Botões

| Tipo | Padding | BG | Border | Texto |
|------|---------|----|--------|-------|
| Primário | `10px 20px` | `--accent` | — | `#fff`, `600` |
| Outline | `10px 20px` | transparente | `--border` | `--text-h` |
| Ghost | `8px 12px` | transparente | — | `--text` (hover: `--text-h`) |
| Danger | `10px 20px` | `--error-bg` | `--error-border` | `--error-text` |

- Radius: `8px` (`--radius-md`)
- Transição: `all 150ms ease-out`
- Disabled: opacidade `0.5`, cursor `not-allowed`

### 4.4 Badges

- Padding: `4px 10px`
- Radius: `6px` (`--radius-sm`)
- Font: `12px`, `600`
- Cor varia com contexto (success/accent/highlight)

### 4.5 Inputs

- Padding: `10px 12px`
- Border: `1px solid --border`
- Focus: `--accent-border` + `box-shadow: 0 0 0 3px var(--accent-light)`
- Radius: `8px`
- Label: `12px 500` acima do input

---

## 5. Ícones

- **Livraria:** `lucide-react` (consistente, Feather-style, SVGs puras)
- Tamanho padrão: `20px` em botões, `16px` em labels, `24px` em navegação
- Cor: herda `currentColor` do elemento pai
- Nunca usar ícones soltos sem contexto semântico (sempre acompanhados de texto ou aria-label)

### Ícones comuns

| Contexto | Ícone Lucide |
|----------|-------------|
| Extração | `ScanLine`, `FileUp` |
| Dashboard | `LayoutDashboard` |
| Nota fiscal | `Receipt`, `FileText` |
| QR Code | `QrCode` |
| Login | `LogIn`, `Mail` |
| Sucesso | `CheckCircle` |
| Erro | `AlertCircle` |
| Economia | `TrendingUp`, `PiggyBank` |
| Valor | `DollarSign` |
| Data | `Calendar` |
| Cópia | `Copy` |
| Abrir link | `ExternalLink` |
| Menu | `Menu` |
| Fechar | `X` |
| Voltar | `ArrowLeft` |
| Config | `Settings` |

---

## 6. Sombras

| Token | Light | Dark | Uso |
|-------|-------|------|-----|
| `--shadow-xs` | sutil | sutil | Inputs, badges |
| `--shadow-sm` | leve | leve | Cards padrão |
| `--shadow-md` | média | média | Modais, dropdowns |
| `--shadow-lg` | alta | alta | Diálogos, notificações |
| `--shadow-accent` | verde brilho | verde brilho | Botão primário (hover) |

---

## 7. Animações

- **Easing:** `cubic-bezier(0.16, 1, 0.3, 1)` — saída natural, sem exageros
- **Duração padrão:** `200ms`
- **Duração rápida:** `120ms` (hover, focus)
- **Quando animar:** hover de cards, entrada de modais (fade + scale), transição de páginas, feedback de ação (copiar, salvar)
- **Quando NÃO animar:** scroll, resize de janela, mudanças de rota instantâneas

---

## 8. Responsividade

| Faixa | Comportamento |
|-------|---------------|
| > 900px | Layout normal, grids de 2-3 colunas, sidebar visível |
| 700-900px | Grids colapsam para 2 colunas, padding reduzido |
| < 700px | Tudo em 1 coluna, navegação vira bottom sheet/menu hamburger, padding lateral `16px` |

---

## 9. Dark Mode

- Detectado por `prefers-color-scheme: dark`
- **Nunca** usar `#000` puro como fundo — o tom mais escuro é `#0f172a` (slate-900)
- Cards em dark mode usam `#1e293b` (slate-800) para criar hierarquia
- Verde accent em dark mode clareia para `#34d399` (melhor contraste em fundo escuro)
- Sombras em dark mode são mais opacas e difusas

---

## 10. Navegação

- **Header sempre visível** em telas > 700px
- **Mobile:** NavBar vira bottom navigation ou drawer
- **Logo:** SVG minimalista (raio/faísca) + logotipo "audime" em letras minúsculas
- **Indicador de rota ativa:** barra vertical ou underline accent
- **Logout:** tom danger suave, confirmar ação

---

## 11. Guidelines de Conteúdo

- **Tom:** amigável mas profissional. Tratar o usuário por "você"
- **Erros:** explicar o que aconteceu + o que fazer. Nunca "erro desconhecido"
- **Valores:** sempre formatados em BRL com centavos. Preto e verde para positivo, vermelho para negativo
- **Datas:** formato BR completo (`20 de jun de 2026`). Em tabelas: `20/06/2026`
- **Empty states:** ilustração + mensagem útil + call to action (nunca só "nada aqui")

---

## 12. Checklist de Consistência

- [ ] Botões primários sempre usam `--accent` como bg
- [ ] Valores monetários sempre usam `formatBRL()` ou `Intl`
- [ ] Ícones sempre de `lucide-react`, nunca SVG inline avulso
- [ ] Dark mode testado em todas as telas antes de lançar
- [ ] Animações respeitam `prefers-reduced-motion`
- [ ] Inputs têm label visível (nunca só placeholder)
- [ ] Todo link com `target="_blank"` tem `rel="noopener noreferrer"`
- [ ] Badges de status seguem o mapa semântico (success/accent/highlight)
