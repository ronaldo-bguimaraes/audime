# Audime Constitution

Gestão detalhada de gastos pessoais: extração de NFC-e (SEFAZ), normalização em
camadas e dashboard financeiro, com API, web e mobile.

**Version**: 1.0.0 | **Ratified**: 2026-10-27 | **Last Amended**: 2026-10-27

## Core Principles

### I. Spec-First (NON-NEGOTIABLE)

Nenhuma implementação começa sem uma especificação com critérios binários e
verificáveis. Todo critério declara seu comando de verificação — se não dá para
observar o resultado por um comando determinístico, o critério não existe.

- Fluxo: `/speckit.specify` → `/speckit.clarify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`.
- Ambiguidade sobre comportamento esperado é resolvida na spec, não no código.
- Decisões de semântica de dados (ex.: elemento ausente = `0` vs `None`) devem
  estar explícitas na spec.

### II. Test-First (NON-NEGOTIABLE)

O teste define o comportamento antes da implementação.

- Escrever o teste que falha → confirmar a falha → implementar até passar.
- Implementação se adapta ao teste; teste nunca é ajustado para acomodar código.
- Testes de parser usam HTML real (`tests/fixtures/nfce_{uf}.html`), não fixtures
  simplificadas — fixtures falsas produzem falso negativo.

### III. Full Regression Gate

"Não quebrou" só existe com evidência.

- `pytest` completo verde antes de qualquer commit (baseline: **81 testes**).
- Qualquer mudança em regra, módulo compartilhado ou schema re-executa os testes
  relacionados, mesmo que pareçam independentes.
- Os testes exigem infraestrutura: Postgres em `localhost:5433` e Redis em
  `localhost:6379`. Suíte sem essa infra não é evidência de nada.
- Testes de frontend (`@playwright/test`) só contam com backend de pé ou API mockada.

### IV. Security by Default

- **Nenhum segredo no repositório nem no histórico.** `.env` é ignorado; toda
  credencial nova vira variável de ambiente.
- Varredura de credenciais obrigatória antes de cada commit (staged e histórico).
- Só `.env.example` é versionado, e com placeholders.
- URL fornecida por usuário é entrada hostil (SSRF): validar esquema, domínio da
  SEFAZ e bloquear IPs privados/loopback antes de qualquer download.
- Redis não tem autenticação: bind sempre em loopback, nunca publicado.
- Acesso público passa exclusivamente pelo Cloudflare Tunnel; nenhuma porta
  interna é exposta na internet.

### V. Reproducible Deploy

O que roda em produção é o que está commitado.

- `docker compose build` precisa funcionar da raiz do repositório: a imagem `web`
  depende do workspace `shared` e do `package-lock.json` raiz.
- Migrações são explícitas (`alembic upgrade head`), nunca implícitas no boot.
- `APP_ENV=production` em produção — em `development` o código de login não é
  enviado por e-mail.
- Deploy documentado em `docs/deploy-tunnel.md`.

### VI. Simplicity and No-Downgrade

- A menor mudança que satisfaz a spec, no escopo que ela define.
- Nenhuma iteração relaxa uma regra de segurança, qualidade ou teste existente.
- Preferir remover código a adicionar abstração sem necessidade comprovada.
- Dependência nova exige justificativa na spec/plan.

### VII. Evidence-Based Done

Uma tarefa está concluída quando o comando que a verifica foi executado e o
resultado está registrado — não quando parece pronta.

- Toda task gerada por `/speckit.tasks` carrega seu critério de verificação.
- `/speckit.analyze` deve rodar antes do `/speckit.implement` em features que
  tocam autenticação, migrações ou pagamento/integrações externas.

## Stack and Architecture Constraints

| Camada | Tecnologia |
| --- | --- |
| API | Python 3.14 + FastAPI, SQLAlchemy 2, Alembic |
| Banco | PostgreSQL (Neon), schemas `raw → staging → core → analytics` |
| Fila | Redis + ARQ (`app/workers/arq_settings.py`) |
| Storage | Cloudflare R2 (arquivos nunca no banco) |
| Web | React 19 + Vite + TypeScript, consome o workspace `shared/` |
| Mobile | React Native (Expo SDK 57) + expo-router, mesmo `shared/` |
| Auth | JWT (HS256) + código de verificação por e-mail |

Regras estruturais:

- **Sem CORS**: no browser, tudo é same-origin — o nginx serve a SPA e faz proxy
  de `/v1/` para o backend.
- **Camadas não se pulam**: `raw` recebe o bruto, `staging` normaliza, `core`
  é entidade de negócio, `analytics` é consumo (inclusive SCD2).
- **Parser por UF** registrado em `app/services/parser_nfce/__init__.py`; novo
  estado exige fixture real + testes.
- **`raw` é append-only**: histórico preservado; correção acontece nas camadas
  seguintes.
- **Banco é externo** (Neon) — não existe serviço `postgres` no `docker-compose.yml`
  de produção; o compose de teste usa `docker-compose.test.yml`.

## Development Workflow and Quality Gates

```
/speckit.specify  →  /speckit.plan  →  /speckit.tasks  →  /speckit.implement
      │                   │                 │
      └─ critérios        └─ decisões       └─ tasks com verificação
        verificáveis        técnicas
```

Gates, em ordem — nenhum é opcional:

1. **Spec com critérios** — sem critério verificável, não há feature.
2. **Teste falhando** — comportamento definido antes da implementação.
3. **Regressão completa** — `pytest` verde.
4. **Build** — `npm --workspace web run build` (inclui `tsc -b`) verde quando o
   web é tocado.
5. **Segurança** — varredura de credenciais + revisão de exposição de portas.

Comandos de referência:

```bash
docker compose -f docker-compose.test.yml up -d    # Postgres :5433
docker compose up -d redis                         # Redis :6379
.venv/bin/python -m pytest -q                      # suíte completa
docker compose build                               # imagens de produção
```

Contexto de feature: artefatos vivem em `specs/NNN-slug/` (`spec.md`, `plan.md`,
`tasks.md`, `research.md`, `contracts/`), versionados com o código.

## Governance

- Esta constituição prevalece sobre preferências de ferramenta, estilo ou hábito.
- Emenda: `/speckit.constitution` + justificativa no PR, com bump de versão
  (MAJOR: princípio removido/redefinido; MINOR: princípio novo; PATCH: clareza).
- Toda revisão/PR verifica conformidade com os princípios; violação exige emenda
  explícita, não exceção silenciosa.
- Complexidade adicionada precisa ser justificada por requisito, não por gosto.
- `docs/deploy-tunnel.md` e `docs/commit-flow.md` são a referência operacional;
  em caso de conflito com esta constituição, a constituição vence.
