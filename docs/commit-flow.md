# Fluxo de Commit e Push

> Do código modificado ao push, com os gates da constituição aplicados.
> Regras: `.specify/memory/constitution.md`.

```
[1] Implementar (TDD)
        │
        ▼
[2] Testes verdes (regressão completa)
        │
        ▼
[3] Varredura de segurança
        │
        ▼
[4] git add (só o que foi intencionado)
        │
        ▼
[5] git commit (Conventional Commits)
        │
        ▼
[6] git push
```

## Step 1: Implementar

- TDD: o teste falha antes, o código vem depois.
- Uma mudança lógica por commit; não expandir escopo além da spec
  (`specs/NNN-slug/spec.md`).

## Step 2: Testes

A suíte exige infraestrutura:

```bash
docker compose -f docker-compose.test.yml up -d   # Postgres :5433
docker compose up -d redis                        # Redis :6379

.venv/bin/python -m pytest -q
```

Se o web/mobile foi tocado:

```bash
docker compose build web      # tsc -b + vite build
```

**Regra:** teste vermelho, nada de commit. Voltar ao Step 1.

## Step 3: Varredura de segurança

Obrigatória antes **de cada** commit:

```bash
# .env fora do controle de versão
git check-ignore -q .env && echo "OK: .env ignorado" || echo "FALHA: .env rastreável"

# Nada de segredo no que está indo para o commit
git diff --cached | grep -inE '(ghp_|gho_|sk-[a-zA-Z0-9]{16,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY|(secret|password|token|api[_-]?key)[[:space:]]*[:=][[:space:]]*["'"'"']?[A-Za-z0-9_\-]{16,})' && echo "FALHA: possível credencial" || echo "OK: diff limpo"

# Nada de segredo no histórico recente
git log --all -p -n 50 | grep -inE '(ghp_|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY)' || echo "OK: histórico limpo"
```

Se aparecer algo: **remover do commit**, rotacionar a credencial e, se já foi
publicada, limpar o histórico. Não existe "commit temporário com segredo".

Também confirmar que nada novo ficou exposto:

```bash
docker compose ps                                   # portas publicadas
grep -nE '127\.0\.0\.1|0\.0\.0\.0' docker-compose.yml
```

## Step 4: git add

```bash
git status
git diff
git add caminho/do/arquivo.py caminho/do/teste.py
```

Nunca `git add .` sem revisar o que entrou.

## Step 5: git commit

```
<tipo>(<escopo>): <descrição>

<corpo opcional — o porquê, não o quê>
```

### Tipos

| Tipo | Quando usar |
|---|---|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Documentação |
| `refactor` | Mudança estrutural sem mudar comportamento |
| `perf` | Performance |
| `test` | Teste adicionado/corrigido |
| `chore` | Manutenção (deps, config, build) |
| `ci` | Pipeline |
| `style` | Formatação/visual (sem lógica) |

### Escopos

| Escopo | Área |
|---|---|
| `api` | Endpoints e schemas FastAPI |
| `parser` | Parsers de NFC-e |
| `db` | Models, schemas, migrações |
| `worker` | Fila ARQ e tasks |
| `auth` | Autenticação/JWT/e-mail |
| `web` | Frontend React |
| `mobile` | App Expo |
| `shared` | Pacote compartilhado |
| `deploy` | Compose, Dockerfile, tunnel |
| `docs` | Documentação |
| `spec` | Artefatos do spec-kit (`specs/`) |

### Regras

1. Título ≤ 50 caracteres, sem ponto final.
2. Imperativo: "Add feature" (não "Added"/"Adding").
3. O corpo explica o **porquê**.
4. Commits atômicos.
5. Linhas do corpo ≤ 72 caracteres.
6. Breaking change: `!` após tipo/escopo — `refactor(api)!: remover endpoint legado`.

### Exemplos

```
feat(auth): add Google ID token login

Passwordless email is friction for returning users. Validating the
ID token server-side keeps a single JWT format for both flows.
```

```
fix(parser): return None when item table is absent

Zero and "unknown" are different answers; analytics summed the wrong
one. Absent data must stay absent through the layers.
```

```
docs(spec): rewrite workflow for spec-kit
```

## Step 6: git push

```bash
git push
```

Só depois dos steps anteriores.

## Convenção de Branches

```
<tipo>/#<numeroIssue>-<alias>
```

| Branch | Descrição |
|---|---|
| `feat/#21-remodelagem-design` | Remodelagem visual |
| `fix/#12-url-truncada` | Correção de URL truncada |
| `docs/#10-workflow` | Documentação do fluxo |
| `style/#8-refresh-login` | Ajuste visual na tela de login |

Toda branch referencia uma issue. Features do spec-kit criam branch própria
(`NNN-slug`) — nesse caso a issue correspondente é a da feature.

## Checklist pré-commit

- [ ] Teste novo falhou antes da implementação
- [ ] `pytest` completo verde
- [ ] Build do web verde (se aplicável)
- [ ] Varredura de segurança limpa (Step 3)
- [ ] `git diff --staged` revisado — só arquivos intencionados
- [ ] Mensagem no formato correto

## Ver também

- `docs/workflow.md` — ciclo completo e gates
- `docs/github-cli-workflow.md` — issues e project board
- `.specify/memory/constitution.md` — princípios e requisitos de segurança
