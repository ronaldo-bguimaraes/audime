# GitHub CLI Workflow

> Como usar o GitHub CLI (`gh`) para gerenciar issues e project boards no projeto **audime**.

---

## Pré-requisitos

- [GitHub CLI](https://cli.github.com/) instalado e autenticado
- Token com escopos: `repo`, `project`, `read:org`, `gist`

```bash
gh auth status
```

Ver escopos atuais:
```bash
gh auth status 2>&1 | grep "Token scopes"
```

---

## Project Board — "audime" (#5)

### Dados do Projeto

| Campo | Valor |
|-------|-------|
| Título | audime |
| Número | `5` |
| Owner | `ronaldo-bguimaraes` (user) |
| ID interno | `PVT_kwHOA-7nDs4Ba3n_` |
| Visibilidade | Público |
| URL | https://github.com/users/ronaldo-bguimaraes/projects/5 |

### Status Disponíveis (Single Select)

| Status | Option ID |
|--------|-----------|
| `Backlog` | `f75ad846` |
| `In Progress` | `47fc9ee4` |
| `In Review` | `c3afecb3` |
| `Done` | `98236657` |

### Field ID do Status

```
PVTSSF_lAHOA-7nDs4Ba3n_zhVsHcI
```

---

## Comandos Úteis

### Issues

#### Listar issues abertas

```bash
gh issue list --limit 20
```

#### Criar uma issue

```bash
gh issue create \
  --title "Título da issue" \
  --body "Descrição detalhada" \
  --label "enhancement" \
  --assignee @me
```

`--label` pode ser: `bug`, `enhancement`, `epic`, `documentation`, etc.
Para múltiplos labels: `--label "bug,enhancement"`.

#### Ver detalhes de uma issue

```bash
gh issue view <número>
```

#### Fechar issue

```bash
gh issue close <número>
```

---

### Project Board

#### Listar projetos do owner

```bash
gh project list --owner ronaldo-bguimaraes
```

#### Listar itens do project board #5

```bash
gh project item-list 5 --owner ronaldo-bguimaraes
```

Formato JSON:
```bash
gh project item-list 5 --owner ronaldo-bguimaraes --format json
```

#### Adicionar issue existente ao project board

```bash
gh project item-add 5 --owner ronaldo-bguimaraes --url "https://github.com/ronaldo-bguimaraes/audime/issues/<número>"
```

#### Mover card para outro status

```bash
gh project item-edit 5 --owner ronaldo-bguimaraes \
  --item-id "<item-id>" \
  --field-id "PVTSSF_lAHOA-7nDs4Ba3n_zhVsHcI" \
  --single-select-option-id "<option-id>"
```

Onde:
- `--item-id` é o ID do item (ex: `PVTI_lAHOA-7nDs4Ba3n_zgx00V0`)
- `--field-id` é o ID do campo Status (fixo)
- `--single-select-option-id` é o ID da opção de status

**Exemplo prático — mover issue #19 para "Done":**

```bash
# 1. Obter item-id da issue
gh project item-list 5 --owner ronaldo-bguimaraes --format json | \
  python3 -c "import sys,json; items=json.load(sys.stdin)['items']; \
  [print(i['id']) for i in items if i['content']['number']==19]"

# 2. Mover para Done (option-id: 98236657)
gh project item-edit 5 --owner ronaldo-bguimaraes \
  --item-id "PVTI_lAHOA-7nDs4Ba3n_zgx00V0" \
  --field-id "PVTSSF_lAHOA-7nDs4Ba3n_zhVsHcI" \
  --single-select-option-id "98236657"
```

#### Criar issue e adicionar ao project board em um passo

```bash
# 1. Criar a issue
gh issue create \
  --title "Minha nova feature" \
  --body "Descrição..." \
  --label "enhancement"

# 2. Copiar o número da issue do output, depois adicionar ao board
ISSUE_NUM=<número>
gh project item-add 5 --owner ronaldo-bguimaraes \
  --url "https://github.com/ronaldo-bguimaraes/audime/issues/$ISSUE_NUM"

# 3. Mover para In Progress (option-id: 47fc9ee4)
#    Primeiro: obter o item-id
gh project item-list 5 --owner ronaldo-bguimaraes --format json | \
  python3 -c "import sys,json; items=json.load(sys.stdin)['items']; \
  [print(i['id']) for i in items if i['content']['number']==$ISSUE_NUM]"

#    Depois: mover
gh project item-edit 5 --owner ronaldo-bguimaraes \
  --item-id "<item-id>" \
  --field-id "PVTSSF_lAHOA-7nDs4Ba3n_zhVsHcI" \
  --single-select-option-id "47fc9ee4"
```

---

## Script de Atalho: Criar Issue + Board

Use o comando abaixo para criar issue e adicionar ao board #5 em um único comando:

```bash
# Cria issue, captura o número, adiciona ao board e move para "In Progress"
ISSUE_URL=$(gh issue create --title "$1" --body "$2" --label "$3" --json url -q '.url')
ISSUE_NUM=$(echo $ISSUE_URL | grep -oP '\d+$')
echo "Issue #$ISSUE_NUM criada: $ISSUE_URL"

# Adicionar ao project board
gh project item-add 5 --owner ronaldo-bguimaraes --url "$ISSUE_URL"

# Obter item-id e mover para "In Progress"
sleep 1
ITEM_ID=$(gh project item-list 5 --owner ronaldo-bguimaraes --format json | \
  python3 -c "import sys,json; items=json.load(sys.stdin)['items']; \
  print([i['id'] for i in items if i['content']['number']==$ISSUE_NUM][0])")
gh project item-edit 5 --owner ronaldo-bguimaraes \
  --item-id "$ITEM_ID" \
  --field-id "PVTSSF_lAHOA-7nDs4Ba3n_zhVsHcI" \
  --single-select-option-id "47fc9ee4"
echo "Issue movida para 'In Progress' no board #5"
```

---

## Mapa: Status do Board vs Passos do Sprint

| Passo do Sprint | Status no Board |
|-----------------|-----------------|
| Refinement (Step 1) | `Backlog` |
| Discovery & Plan (Step 2) | `In Progress` |
| Test Spec (Step 3) | `In Progress` |
| Development (Step 4) | `In Progress` |
| Validation (Step 5) | `In Review` |
| Review & Archive (Step 6) | `Done` |

---

## Referências

- [GitHub CLI — `gh project`](https://cli.github.com/manual/gh_project)
- [GitHub CLI — `gh issue`](https://cli.github.com/manual/gh_issue)
- [GitHub Projects (V2) API](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects)
