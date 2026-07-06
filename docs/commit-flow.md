# Fluxo de Commit e Push

> Processo completo desde a modificação do código até o push, com segurança integrada.

---

## Ciclo de Trabalho

```
[1] Modificar código
        │
        ▼
[2] Executar testes (pytest)
        │
        ▼
[3] Varredura de segurança (@devops_engineer)
        │
        ▼
[4] git add (apenas arquivos intencionados)
        │
        ▼
[5] git commit (formato padronizado)
        │
        ▼
[6] git push
```

---

## Step 1: Modificar Código

- Seguir TDD: primeiro o teste falha, depois a implementação
- Manter escopo limitado: uma mudança lógica por vez
- Não expandir escopo além do necessário para satisfazer os testes

---

## Step 2: Executar Testes

Sempre executar a suíte completa antes de commitar:

```bash
pytest tests/ -v
```

Se houver testes de frontend:

```bash
cd web && npm test
```

**Regra:** Se algum teste falhar, não commitar. Voltar ao Step 1.

---

## Step 3: Varredura de Segurança

**Obrigatório antes de todo commit.** Ativar `devops_engineer` ou executar:

```bash
# Verificar se .env está no .gitignore
grep -q "^\.env$" .gitignore && echo "✅ .env no .gitignore" || echo "❌ .env NÃO está no .gitignore"

# Verificar histórico por credenciais
git log --all -p | grep -iE '(ghp_|sk-[a-zA-Z0-9]|AKIA[0-9A-Z]{16}|secret.*=|password.*=|token.*=)' || echo "✅ Nenhuma credencial encontrada no histórico"

# Verificar diff do staged para credenciais
git diff --cached | grep -iE '(ghp_|sk-[a-zA-Z0-9]|AKIA[0-9A-Z]{16}|secret.*=|password.*=|token.*=)' || echo "✅ Nenhuma credencial no staged"
```

Se o `devops_engineer` (ou scan manual) flagar algo, **resolver antes de prosseguir**.

---

## Step 4: git add

Adicionar **apenas** os arquivos intencionados:

```bash
# Verificar o que mudou
git status
git diff

# Adicionar arquivos específicos
git add caminho/para/arquivo.py
git add caminho/para/test_arquivo.py

# NUNCA fazer git add . sem antes revisar
```

---

## Step 5: git commit

Formato obrigatório:

```
<tipo>(<escopo>): <descrição>

<corpo opcional — explica o porquê>

<rodapé opcional>
```

### Tipos

| Tipo | Quando usar |
|------|-------------|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Documentação |
| `refactor` | Mudança estrutural sem mudança de comportamento |
| `perf` | Melhoria de performance |
| `test` | Adição ou correção de teste |
| `chore` | Manutenção (deps, config, build) |
| `ci` | CI/CD |
| `style` | Formatação (sem mudança de lógica) |

### Escopos

| Escopo | Área |
|--------|------|
| `cycle` | Ciclo do orchestrator |
| `agents` | Definições de agentes |
| `adapter` | Adaptadores de ferramenta |
| `docs` | Documentação do projeto |
| `spec` | Especificação do ciclo |
| `policy` | Políticas de segurança |

### Regras

1. Título ≤ 50 caracteres, sem ponto final
2. Modo imperativo: "Add feature" (não "Added" ou "Adding")
3. Corpo explica o **porquê** — o **o quê** já está no diff
4. Commits atômicos: uma mudança lógica por commit
5. Linhas do corpo ≤ 72 caracteres
6. Breaking changes: usar `!` após tipo/escopo: `refactor(api)!: remove legacy endpoint`

### Exemplos

```
feat(agents): add specification agent preflight mode
```

```
refactor(cycle): simplify from 8 to 5 steps

Dedicated docs step created overhead without adding traceability.
Merging it into inquiry makes docs a continuous side-effect.
```

```
docs(commits): add commit conventions
```

---

## Step 6: git push

```bash
git push origin <branch>
```

Para branch atual:

```bash
git push
```

**Regra:** Só fazer push se todos os steps anteriores passarem.

---

## Convenção de Branches

| Tipo | Formato | Exemplo |
|------|---------|---------|
| Feature | `feat/<descricao>` | `feat/add-qrcode-scanner` |
| Bug fix | `fix/<descricao>` | `fix/dashboard-empty-state` |
| Docs | `docs/<descricao>` | `docs/sprint-workflow` |
| Refactor | `refactor/<descricao>` | `refactor/parser-architecture` |

---

## Checklist Pré-Commit

- [ ] Testes passam (`pytest tests/ -v`)
- [ ] Lint passa (`ruff check .`)
- [ ] Typecheck passa (`pyright app/ tests/` ou `npx tsc --noEmit`)
- [ ] `@devops_engineer` — nenhuma credencial vazada
- [ ] `git diff` revisado — apenas arquivos intencionados
- [ ] Mensagem de commit no formato correto

---

## Ver Também

- `.agents/workspace/commit_conventions.md` — Definição canônica
- `docs/workflow-sprint.md` — Fluxo completo de sprint
- `docs/github-cli-workflow.md` — Como criar issues e gerenciar boards
- `.agents/agents/devops_engineer.md` — Escaneamento de segurança
