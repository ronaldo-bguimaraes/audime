# Audime — Spec-Driven Development

Extração de NFC-e (SEFAZ) → normalização em camadas → dashboard financeiro.
API FastAPI + Postgres, web React/Vite e mobile Expo compartilhando `shared/`.

O desenvolvimento segue **Spec-Driven Development** com [GitHub Spec Kit](https://github.com/github/spec-kit).
A fonte de verdade das regras é a constituição: `.specify/memory/constitution.md`.

## Fluxo

```
/speckit.specify → /speckit.clarify → /speckit.plan → /speckit.tasks → /speckit.analyze → /speckit.implement
```

| Comando | Quando usar |
| --- | --- |
| `/speckit.constitution` | Criar/emendar princípios do projeto (raro) |
| `/speckit.specify` | Nova feature: gera `specs/NNN-slug/spec.md` com critérios |
| `/speckit.clarify` | Antes de planejar: resolve ambiguidade da spec |
| `/speckit.plan` | Decisões técnicas, `plan.md`, `research.md`, `contracts/` |
| `/speckit.tasks` | Quebra em tasks executáveis com critério de verificação |
| `/speckit.analyze` | Auditoria de consistência spec ↔ plan ↔ tasks |
| `/speckit.implement` | Executa as tasks (TDD) |
| `/speckit.checklist` | Checklist de qualidade da feature |
| `/speckit.taskstoissues` | Publica as tasks como issues no GitHub |

Artefatos de uma feature ficam em `specs/NNN-slug/` e são versionados com o código.

## Não-negociáveis

Resumo da constituição — em caso de dúvida, leia `.specify/memory/constitution.md`.

1. **Spec-first** — nenhuma implementação sem critério binário e verificável.
2. **Test-first** — o teste falha antes de existir implementação; o teste manda.
3. **Regressão completa** — `pytest` verde antes de commitar.
4. **Segurança** — nenhum segredo no repo; varredura de credenciais antes do commit;
   URL de usuário é entrada hostil (SSRF).
5. **Deploy reprodutível** — `docker compose build` da raiz tem que funcionar.
6. **Simplicidade / no-downgrade** — menor mudança possível, nenhuma regra relaxada.
7. **Done com evidência** — tarefa só fecha com o comando de verificação executado.

## Comandos

```bash
# Infra de teste (obrigatória: sem ela a suíte não é evidência)
docker compose -f docker-compose.test.yml up -d    # Postgres :5433
docker compose up -d redis                         # Redis :6379

# Testes (baseline: 81)
.venv/bin/python -m pytest -q

# Web (build + typecheck)
docker compose build web        # roda tsc -b + vite build no container

# Stack completo + tunnel
./deploy.sh
```

## Layout

```
app/            API FastAPI (api/, core/, services/, workers/)
abstract/       models e engine SQLAlchemy (schemas raw/staging/core/analytics)
alembic/        migrações (explícitas: alembic upgrade head)
shared/         tipos + API client + utils usados por web e mobile
web/            React 19 + Vite (build a partir da raiz — workspace)
mobile/         Expo SDK 57 + expo-router
tests/          pytest (fixtures NFC-e reais em tests/fixtures/)
specs/          features do spec-kit (spec/plan/tasks)
.specify/       spec-kit: constituição, templates, scripts, workflows
docs/           arquitetura, PRD, deploy, knowledge, records
```

## Referências

- `docs/workflow.md` — ciclo completo e gates
- `docs/commit-flow.md` — Conventional Commits + varredura de segurança
- `docs/github-cli-workflow.md` — issues e project board
- `docs/deploy-tunnel.md` — deploy self-hosted via Cloudflare Tunnel
- `docs/knowledge/` — conhecimento técnico acumulado (Alembic, ARQ, Playwright…)
- `docs/records/` — histórico de features e decisões

## Estado atual (contexto honesto)

- Backend: 81 testes verdes; parsers MT e MG.
- Web: dashboard com Recharts, extração com QR Code, design system aplicado.
- Mobile: em andamento (issue #25); tela de detalhe da nota ainda não roteada.
- Pendências conhecidas: login com Google (#3) não iniciado; allowlist de domínios
  SEFAZ para SSRF ainda não implementada; CI não roda `pytest` nem `tsc`.
