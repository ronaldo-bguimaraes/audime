# Knowledge

Conhecimento técnico durável sobre o Audime: tecnologias, bibliotecas, padrões e
armadilhas já investigadas. O objetivo é não reaprender o mesmo problema duas vezes.

## O que entra aqui

- Pesquisa sobre uma tecnologia e como ela se aplica **neste** projeto
  (ex.: Alembic, ARQ, Playwright, `qr-scanner`).
- Decisões técnicas com alternativas descartadas e o motivo.
- Armadilhas de biblioteca/ambiente que custaram tempo para descobrir.

O que **não** entra aqui: critérios de uma feature (vão em `specs/NNN-slug/spec.md`)
e o histórico de entrega (vai em `docs/records/`).

## Formato

```markdown
---
date: YYYY-MM-DD
topic: <tópico>
tags: [tag1, tag2]
sources:
  - title: <título>
    url: <url>
---

# <Tópico> — <data>

## What is it
## How we would use it in Audime
## Alternatives
## Pros and cons
## Conclusion
```

| Campo | Obrigatório | Descrição |
|---|---|---|
| `date` | sim | Data da pesquisa (YYYY-MM-DD) |
| `topic` | sim | Nome do tópico |
| `tags` | sim | Tags para busca |
| `sources` | sim | Fontes consultadas |

## Nomenclatura

`<topico>.md`, minúsculas com hífens (`docker.md`, `pydantic-v2.md`). Para assuntos
longos, divida em partes: `alembic_part1_fundamentals.md`.

## Quando criar

Ao final de uma task em que você teve que pesquisar algo que vai valer para as
próximas features. Custa cinco minutos agora e evita retrabalho depois. Escreva em
português, com exemplos do próprio Audime.

## Índice

| Documento | Assunto |
|---|---|
| `alembic_part1_fundamentals.md` | Fundamentos de migrações |
| `alembic_part2_configuration.md` | Configuração do Alembic |
| `alembic_part2b_schema_handling.md` | Schemas Postgres nas migrações |
| `alembic_part3_operations.md` | Operações e deploy de migração |
| `alembic_part3b_best_practices.md` | Boas práticas |
| `arq_part1_overview.md` | Fila ARQ: visão geral |
| `arq_part2_implementation.md` | Implementação dos workers |
| `arq_part2b_risks_alternatives.md` | Riscos e alternativas |
| `playwright-route-glob-patterns.md` | Glob patterns de rotas no Playwright |
