# Lições Aprendidas

<!-- Acumuladas entre ciclos. Toda falha vira lição aqui. -->

## Ciclo 1 — Segurança + Correção de Imports

### O que funcionou
- A varredura de histórico com `git log -p | grep` é suficiente para projetos pequenos — não precisa de gitleaks/trufflehog
- `rg` é eficaz para encontrar referências residuais após rename de pacote
- `pydantic-settings` com `extra="ignore"` evita falhas por vars extras no `.env`

### O que aprendemos
- O pacote `database` foi renomeado para `abstract` mas os imports não foram atualizados — 8 arquivos quebrados
- `sa.JSONB` não existe no SQLAlchemy 2.0+ — usar `sa.JSON`
- O `.env` sempre esteve no `.gitignore` e nunca foi commitado — boa prática desde o início
- `.env.example` continha `R2_TOKEN` que não é usado pelo `Settings` — foi removido para clareza

### Riscos identificados
- `abstract.engine` importa `app.core.config` — dependência entre pacotes irmãos. Se `app.core.config` um dia importar algo de `abstract`, forma circular import
- Parser NFC-e continua frágil (seletores hardcoded para MT)
- Extração síncrona na request (bloqueia FastAPI)
- Testes com SQLite exigem `schema_translate_map` e `with_variant` para `BigInteger`

## Ciclo 2 — Autenticação sem senha

### O que funcionou
- Arquitetura de `EmailSender` abstrato com `LogEmailSender` permite trocar implementação sem mexer no fluxo
- `PyJWT` com HS256 é simples e direto para MVP
- Rate limiting básico com `AuthCode.attempts` + cooldown de 60s

### O que aprendemos
- Testes com SQLite exigem `schema_translate_map` para ignorar schemas PostgreSQL (`core`, `raw`, etc.)
- `sa.BigInteger` não auto-incrementa no SQLite — usar `with_variant(sa.Integer(), "sqlite")`
- `DateTime(timezone=True)` no SQLite perde timezone — `expires_at.replace(tzinfo=...)` ao comparar
- `HTTPBearer` do FastAPI retorna 401 (não 403) quando token está ausente
- `get_current_user_id()` agora lê do JWT via `Depends(security)` — endpoints protegidos por padrão

## Ciclo 3 — Frontend MVP

### O que funcionou
- Spec-first com 52 critérios verificáveis guiou precisamente a implementação
- CSS Modules (Vite nativo) — zero setup, escopo por componente, sem dependências
- Fetch nativo com wrapper em `api/client.ts` — simples e suficiente para 4 endpoints
- AuthProvider com Context API — eliminou prop drilling do token
- `Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" })` para formatação R$
- Vite proxy (`server.proxy`) para rotear `/v1` para backend em dev
- Contagem regressiva de 60s para reenvio de código com `setInterval` + `clearInterval`

### O que aprendemos
- `react-router` v8 unificou os pacotes: `BrowserRouter`, `Routes`, `Route` agora vêm de `'react-router'` (não `'react-router-dom'`), e há o subpath `'react-router/dom'`
- O ESLint do React 19 com `react-hooks/use-memo` exige que `useCallback`/`useMemo` tenham arrays literais como dependências — não aceita variáveis
- O ESLint do React 19 com `react-hooks/refs` proíbe atualizar `ref.current` durante render (deve ser em `useEffect`)
- O ESLint do React 19 com `react-hooks/set-state-in-effect` proíbe `setState` síncrono no corpo do `useEffect`
- Handler global de 401 que redireciona (`window.location.href`) quebra o fluxo de login se usado em endpoints de auth — solução: apenas remover token e deixar o ProtectedRoute redirecionar
- `pending_email` deve ser lido antes de remover do localStorage
- `react-router/dom` exporta `RouterProvider` e `HydratedRouter` (para SSR/RSC), enquanto os componentes declarativos (`BrowserRouter`, `Routes`, `Route`) estão no pacote principal

### Pendências
- Trocar `LogEmailSender` por SMTP real (Resend, SendGrid, Gmail)
- Adicionar refresh token + rotação
- Adicionar Redis para rate limiting em produção
- Migrar tabela `auth_code` para SQL de produção em `scripts.sql`
- Adicionar headers de segurança (CSP) no nginx em produção
- Adicionar tela de erro 404 customizada

## Ciclo 5 — Criação do Subagent Aprendiz

### O que funcionou
- Pesquisa com questionador + explicador em paralelo revelou issues que a spec não antecipou (Modo Análise é read-only, permissões path-based têm bugs)
- A spec-first + pesquisa + ajuste funcionou: o design final é melhor que o inicial

### O que aprendemos
- O Modo Análise do loopback é **read-only por definição** — agentes que escrevem (como o aprendiz) não devem ser listados lá
- Aprendiz combina pesquisa + questionamento + explicação + registro, mas é o **único agente de pesquisa com permissão de escrita** — isso o diferencia claramente de questionador e explicador
- O formato de lista de subagentes usa **bold** no `.agents/agents/loopback.md` e **backticks** no `.opencode/agents/loopback.md` — estilos diferentes mas consistentes com o contexto de cada arquivo
- A especificação inicial pode conter suposições incorretas que são corrigidas pela pesquisa — o ciclo de questionamento é essencial

## Ciclo 4 — Skills vs Agents

### O que aprendemos
- O critério decisivo entre skill e agent **não é escopo**, mas sim **necessidade de isolamento de contexto**: skills herdam o contexto do agente chamador, agents têm contexto próprio isolado
- Skills são ideais para tarefas **aditivas** (pesquisa, questionamento) que se beneficiam de contexto rico — não para tarefas **críticas** (validação, auditoria) que exigem independência
- O paralelismo (`task()` para múltiplos subagentes simultâneos) é uma vantagem concreta dos agents que skills não replicam — skills são blocos de texto injetados sequencialmente
- O maker-checker split é o princípio arquitetural mais importante do ciclo loopback: **proposer ≠ approver** — e isso exige isolamento de contexto que só agents提供 (com `context: fork` ou contexto fresco)
- Subagentes de pesquisa (questionador, explicador) podem ser unificados em uma skill `pesquisador` sem perda funcional, apenas com perda de paralelismo — tradeoff aceitável se simplicidade for prioridade
- A Skills 2.0 (issue #17791 com `context: fork`, `allowed_tools`) pode mudar completamente esta análise — monitorar para reavaliação
- A migração de agent → skill é custosa (opencode.json, arquivos de definição, AGENTS.md, loopback.md) — só vale se o ganho for claro e mensurável
