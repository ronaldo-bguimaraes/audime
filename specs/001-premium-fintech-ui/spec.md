# Feature Specification: Refatoração Visual — Fintech Premium 2026

**Feature Branch**: `001-premium-fintech-ui`

**Created**: 2026-10-27

**Status**: Draft

**Input**: Refatorar o design visual do web para estética fintech premium 2026 — hierarquia, tipografia, componentes, navegação, tabelas e gráficos sob um único design system coerente, preservando funcionalidade e regras de negócio.

## Contexto

O web do Audime funciona (dashboard, extração, detalhes, login) mas o visual ainda
lê como "dashboard CRUD": accent esmeralda + âmbar decorativo, cards para tudo,
sombras em camadas, CSS por tela (2.085 linhas em 9 arquivos) sem primitivas
compartilhadas. O objetivo é que o produto comunique **"calm financial
intelligence"**: confiável, preciso, analítico, premium.

Referências de direção (não de cópia): Linear, Stripe, Revolut, Monzo, plataformas
de investimento modernas.

**Fora de escopo**: backend, contratos de API, regras de negócio, app mobile.

## User Scenarios & Testing

### User Story 1 - Dashboard que hierarquiza o número que importa (Priority: P1)

Um usuário abre o dashboard e entende em 2 segundos quanto gastou no período. O
valor principal é o elemento dominante; as métricas secundárias apoiam sem competir.
Uma frase contextual explica a variação em relação ao mês anterior, em vez de só
mostrar um gráfico.

**Why this priority**: é a tela de entrada e onde a percepção de "produto premium
vs CRUD" é decidida. Sem isso, o resto é cosmético.

**Independent Test**: abrir `/dashboard` com dados e verificar (a) um único bloco
dominante com o total, (b) secundárias visualmente subordinadas, (c) insight
textual presente quando há ≥2 meses de dados, (d) nenhum card com peso igual ao
hero.

**Acceptance Scenarios**:

1. **Given** resumo com `valor_total > 0`, **When** o dashboard carrega, **Then**
   o total do período é o maior elemento tipográfico da tela e aparece antes de
   qualquer métrica secundária no DOM.
2. **Given** `por_mes` com ≥2 meses, **When** o dashboard carrega, **Then** existe
   uma frase de insight com a variação percentual vs mês anterior, com sinal e
   cor semântica (verde = gastou menos, vermelho = gastou mais).
3. **Given** dados vazios, **When** o dashboard carrega, **Then** aparece um empty
   state informativo com a próxima ação ("extrair primeira nota"), sem cards ou
   gráficos vazios.

### User Story 2 - Sistema visual consistente em todas as telas (Priority: P2)

Login, Dashboard, Extrair, Detalhe da Extração e Detalhe da Nota compartilham as
mesmas primitivas (botão, input, tabela, badge, card, skeleton). Trocar de tela não
muda raio, sombra, tipografia ou espaçamento.

**Why this priority**: é o que faz o produto parecer intencional. Uma tela fora do
sistema destrói a percepção de qualidade.

**Independent Test**: inspecionar as 5 telas e confirmar que botão/input/tabela
usam as mesmas classes/tokens, e que nenhum `.module.css` define cores hex.

**Acceptance Scenarios**:

1. **Given** qualquer tela, **When** inspeciono os estilos, **Then** 0 valores hex
   de cor fora de `index.css` (tokens).
2. **Given** qualquer tela, **When** comparo raios de card/input, **Then** estão
   no intervalo 10–14px e vêm do mesmo token.
3. **Given** qualquer tela, **When** procuro sombras em cards, **Then** uso apenas
   `--shadow-xs`/`--shadow-sm` (elevação por borda + tint, não por sombra pesada).

### User Story 3 - Fluxo de extração legível e denso (Priority: P3)

A tabela de extrações e as telas de detalhe transmitem competência: linhas densas
mas legíveis, números alinhados à direita com numerais tabulares, status como badge
discreto, timeline do pipeline clara, QR code sem protagonismo excessivo.

**Why this priority**: é o fluxo operacional; densidade mal resolvida é o que mais
denuncia interface amadora.

**Independent Test**: abrir `/extrair` e `/extracao/:id`, verificar alinhamento
numérico, altura de linha e badges consistentes com o resto do app.

**Acceptance Scenarios**:

1. **Given** a lista de extrações, **When** leio a tabela, **Then** colunas
   numéricas são alinhadas à direita com `font-variant-numeric: tabular-nums`.
2. **Given** uma extração em andamento, **When** a tela atualiza, **Then** o
   loading usa skeleton discreto, sem spinner de página inteira nem salto de layout.

### Edge Cases

- Muitos meses no gráfico (≥12): eixo reduz rótulos, sem sobreposição.
- Empresa com nome longo: trunca com ellipsis, sem quebrar a coluna de valor.
- Valores negativos (estorno) mantêm sinal e alinhamento.
- Erro de API: mensagem com ação de retry, no mesmo padrão visual das outras telas.
- Dark mode: todos os pares de token mantêm contraste; gráficos legíveis.
- Contagem de notas = 0 mas total > 0 (dados parciais): não quebrar hierarquia.

## Requirements

### Functional Requirements

- **FR-001**: O sistema visual DEVE ter fonte única de tokens em `web/src/index.css`
  (cor, tipografia, espaçamento, raio, elevação, movimento). Nenhum `.module.css`
  DEVE declarar cor literal.
- **FR-002**: Tipografia DEVE ser sans-serif (Inter, já carregada) com escala de 6
  níveis e `tabular-nums` obrigatório em todo valor monetário/numérico.
- **FR-003**: Elevação DEVE ser comunicada por borda sutil + diferença de superfície;
  sombras só como reforço (`--shadow-xs`, `--shadow-sm`).
- **FR-004**: DEVE existir **um** accent primário; cores semânticas (verde/vermelho)
  só comunicam movimento financeiro positivo/negativo.
- **FR-005**: Dark mode DEVE usar os mesmos nomes de token via
  `prefers-color-scheme`, sem CSS duplicado por componente.
- **FR-006**: O dashboard DEVE ter hierarquia explícita: 1 métrica hero (total do
  período), 2–3 secundárias subordinadas, gráfico como apoio, insight contextual.
- **FR-007**: Insights DEVEM ser derivados dos dados já disponíveis
  (`/v1/dashboard/resumo`), sem novo endpoint nem mudança de backend.
- **FR-008**: Gráficos DEVEM ser mínimos: sem gridline vertical, sem gradiente, sem
  sombra, tooltip discreto, no máximo 2 séries visuais por gráfico.
- **FR-009**: Tabelas DEVEM ser densas (linha 36–44px), com header discreto, hover de
  linha e números alinhados à direita.
- **FR-010**: Navegação DEVE ser uma barra simples e previsível (Dashboard, Extrair,
  sair) com estado ativo inequívoco; nenhuma navegação nova.
- **FR-011**: Empty states DEVEM explicar o estado e oferecer a próxima ação.
- **FR-012**: Loading DEVE usar skeletons para conteúdo e manter o layout estável.
- **FR-013**: Ícones DEVEM ser exclusivamente `lucide-react`, em uma escala de 3
  tamanhos (16/18/20), sem SVG inline novo.
- **FR-014**: Acessibilidade: foco visível em todos os interativos, labels em inputs,
  contraste ≥ 4.5:1 para texto e ≥ 3:1 para elementos de UI.
- **FR-015**: Responsivo até 375px: cards empilham, sem scroll horizontal, tabelas
  viram lista legível.
- **FR-016**: Rotas, fluxos, chamadas de API e regras de negócio DEVEM permanecer
  idênticos (login, dashboard, extrair, extração, nota).
- **FR-017**: Primitivas compartilhadas DEVEM existir para botão, input, tabela,
  badge, card e skeleton — sem CSS duplicado por tela.

### Key Entities

- **Design tokens**: accent, superfícies, texto, bordas, semânticos, escala
  tipográfica, espaçamento, raio, elevação, movimento.
- **Primitivas**: Button (primary/secondary/ghost/danger), Input, Table, Badge
  (neutro/positivo/negativo/andamento), Card, Skeleton, EmptyState.
- **Telas**: Login, Dashboard, Extrair, Detalhe da Extração, Detalhe da Nota.

## Success Criteria

### Measurable Outcomes

- **SC-001**: `grep -rnE "#[0-9a-fA-F]{3,8}" web/src/**/*.module.css` → **0**
  resultados (toda cor vem de token).
- **SC-002**: raios de card/input ∈ [10px, 14px] e definidos em `--radius-*`.
- **SC-003**: `grep -rn "gradient" web/src` → 0 (exceto nenhum); `box-shadow` em
  cards limitado a `--shadow-xs`/`--shadow-sm`.
- **SC-004**: contraste de todos os pares texto/fundo (light e dark) ≥ 4.5:1,
  verificado por script determinístico no repositório.
- **SC-005**: dashboard tem exatamente 1 elemento de métrica hero; a fonte das
  secundárias é ≤ 60% da hero.
- **SC-006**: ≥1 insight textual presente quando `por_mes` tem ≥2 meses, com sinal
  e cor semântica corretos (teste automatizado sobre a função de derivação).
- **SC-007**: `docker compose build web` verde (`tsc -b` + `vite build`).
- **SC-008**: 100% das rotas existentes continuam respondendo e o fluxo de login →
  dashboard → extrair funciona com backend real (smoke manual documentado).
- **SC-009** (emendado após medição): nenhuma tela redefine botão/input/badge —
  todos vêm de `web/src/components/ui/`; e o CSS de módulos fica **≤ 1.900 linhas**
  (medido: 1.883, contra 2.085 antes). O alvo inicial de 1.500 linhas media
  verbosidade de formatação, não coerência: CSS Modules exige um arquivo por
  componente, e comprimir linhas não reduziria duplicação real.
- **SC-010**: `grep -rn "<svg" web/src` → 0 SVG inline novo (ícones via lucide).
- **SC-011**: 375px de largura: `document.documentElement.scrollWidth <= 375` em
  todas as telas.
- **SC-012**: suíte backend permanece 81/81 (nenhuma mudança de lógica).

## Assumptions

- Escopo é **web**; o app mobile mantém o visual atual nesta feature.
- Dark mode segue a preferência do sistema (sem toggle manual na UI nesta versão).
- Intercontinua sendo a fonte (sem custo de licença, já carregada).
- Recharts permanece como biblioteca de gráficos.
- O accent primário continua no espectro esmeralda/violeta definido em `/speckit.clarify`.

## Clarifications

### Session 2026-10-27

- **Q**: Qual accent único? → **A**: Esmeralda (mantém identidade atual). Âmbar deixa de ser decorativo e passa a ser exclusivamente aviso.
- **Q**: Como o usuário escolhe o tema? → **A**: Apenas `prefers-color-scheme` (sem toggle na UI nesta versão).
- **Q**: Escopo? → **A**: Somente web. Mobile recebe spec própria depois, reaproveitando os tokens.
