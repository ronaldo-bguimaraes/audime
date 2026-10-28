# Workflow — Spec-Driven Development

> Ciclo de trabalho do Audime com GitHub Spec Kit.
> Regras: `.specify/memory/constitution.md`. Comandos: `AGENTS.md`.

## Visão geral

```
              ┌──────────────────────────────────────────────────┐
  ideia  ───▶ │ /speckit.specify                                 │
              │   specs/NNN-slug/spec.md  (critérios binários)   │
              └───────────────────┬──────────────────────────────┘
                                  ▼
                    /speckit.clarify   (só se houver ambiguidade)
                                  ▼
              ┌──────────────────────────────────────────────────┐
              │ /speckit.plan                                    │
              │   plan.md · research.md · contracts/ · data-model│
              └───────────────────┬──────────────────────────────┘
                                  ▼
                    /speckit.analyze   (consistência spec ↔ plan)
                                  ▼
              ┌──────────────────────────────────────────────────┐
              │ /speckit.tasks  →  tasks.md (TDD, com verificação)│
              └───────────────────┬──────────────────────────────┘
                                  ▼
                    /speckit.implement  →  código + testes verdes
                                  ▼
                    /speckit.checklist  →  gate final
```

Artifacts de cada feature ficam em `specs/NNN-slug/` (criado pelo
`/speckit.specify`, numeração sequencial).

## Etapas

### 1. Specify

`/speckit.specify <descrição da feature>`

Produz `specs/NNN-slug/spec.md` com:

- contexto e objetivo;
- **critérios de aceite** — cada um observável por um comando;
- casos de borda (ex.: HTML vazio, extração duplicada, usuário sem notas);
- o que está fora de escopo.

Sem critério verificável, a feature não avança (Princípio I).

### 2. Clarify

`/speckit.clarify` — levanta as perguntas que a spec deixou em aberto e grava as
respostas na própria spec. Ambiguidade resolvida aqui custa minutos; resolvida
durante a implementação custa retrabalho.

### 3. Plan

`/speckit.plan` — decisões técnicas, arquivos afetados, contratos de API,
migrações necessárias, estratégia de teste e riscos. Pesquisa técnica durável
vai para `docs/knowledge/`; aqui fica o que é específico da feature.

### 4. Analyze

`/speckit.analyze` — checa consistência entre spec, plan e tasks e aponta
violações da constituição. **Obrigatório** para features que tocam autenticação,
migrações ou integrações externas.

### 5. Tasks

`/speckit.tasks` — quebra o plano em tasks pequenas, ordenadas por dependência,
cada uma com o comando que prova que está pronta. Tasks de teste vêm antes das
tasks de implementação (Princípio II).

### 6. Implement

`/speckit.implement` — executa as tasks em TDD:

1. escrever o teste;
2. rodar e **ver falhar** (falha pelo motivo certo, não por import quebrado);
3. implementar até passar;
4. rodar a regressão completa;
5. marcar a task como concluída com a evidência (comando + resultado).

### 7. Checklist (fechamento)

`/speckit.checklist` — valida a feature contra a spec e a constituição antes do PR.
O PR referencia `specs/NNN-slug/`, não um resumo paralelo.

## Gates

Ordem obrigatória, nenhum opcional:

| # | Gate | Verificação |
|---|---|---|
| 1 | Spec com critérios | `specs/NNN-slug/spec.md` |
| 2 | Teste falhando | `pytest` do teste novo falha antes do código |
| 3 | Regressão | `.venv/bin/python -m pytest -q` (baseline 81) |
| 4 | Build web | `docker compose build web` (`tsc -b` + vite) |
| 5 | Segurança | varredura de credenciais + portas expostas |

Infra de teste é pré-requisito do gate 3:

```bash
docker compose -f docker-compose.test.yml up -d   # Postgres :5433
docker compose up -d redis                        # Redis :6379
```

## GitHub

Cada feature vira uma issue; cada task pode virar issue via
`/speckit.taskstoissues`.

- Labels: `bug`, `enhancement`, `epic`, `documentation`.
- Board #5 ("audime"): `Backlog → In Progress → In Review → Done`.
- Comandos e IDs das colunas: `docs/github-cli-workflow.md`.

Mapeamento com o ciclo:

| Momento | Board |
|---|---|
| Spec aprovada | `Backlog` → `In Progress` |
| PR aberto | `In Review` |
| Merge + gates verdes | `Done` |

## Commits

Conventional Commits, um commit por unidade lógica, com varredura de credenciais
antes de cada um — ver `docs/commit-flow.md`.

## Escopo

Escopo grande é a causa mais comum de sprint sem entrega: uma feature por spec.
Melhorias que surgem durante a implementação viram **nova spec**, não parágrafo
extra na atual.
