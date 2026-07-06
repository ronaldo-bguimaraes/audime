# Token Scopes — GitHub

> Escopos de token necessários para operar o projeto **audime** com GitHub CLI e integrações.

---

## Escopos Mínimos

| Escopo | Finalidade | Obrigatório |
|--------|------------|-------------|
| `repo` | Acesso a repositórios privados/públicos | ✅ Sim |
| `project` | Gerenciar project boards (GitHub Projects V2) | ✅ Sim |
| `read:org` | Ler organizações (se aplicável) | ✅ Sim |
| `gist` | Criar/gerenciar gists | ❌ Opcional |

---

## Verificar Escopos Atuais

```bash
gh auth status 2>&1 | grep "Token scopes"
```

Exemplo de output:
```
Token scopes: 'gist', 'project', 'read:org', 'repo'
```

---

## Como Configurar

1. Acesse [GitHub Settings → Tokens](https://github.com/settings/tokens)
2. Crie um token clássico (classic) ou um fine-grained token
3. Selecione os escopos:
   - `repo` (Full control of private repositories)
   - `project` (Manage projects)
   - `read:org` (Read org membership)
   - `gist` (Create gists) — opcional
4. Autentique no CLI:

```bash
gh auth login
```

Ou configure manualmente:

```bash
gh auth setup-git
export GH_TOKEN=<seu-token>
```

---

## Escopos Fine-Grained (Recomendado)

Se usar fine-grained tokens, as permissões necessárias são:

| Permissão | Nível |
|-----------|-------|
| Repository: Administration | Read |
| Repository: Contents | Read & Write |
| Repository: Issues | Read & Write |
| Repository: Metadata | Read (obrigatório) |
| Organization: Projects | Read & Write |
| Account: Gists | Read & Write (opcional) |

---

## Por Que Cada Escopo?

### `repo`
- Clonar, fazer push/pull
- Criar e gerenciar issues
- Gerenciar PRs
- Acessar GitHub Actions

### `project`
- Criar e mover cards no project board
- Atualizar status de itens
- Gerenciar campos do projeto

### `read:org`
- Listar projetos da organização (quando aplicável)
- Verificar membros

### `gist`
- Criar gists a partir do CLI (uso ocasional)

---

## Ver Também

- `docs/github-cli-workflow.md` — Como usar os escopos na prática
- `docs/commit-flow.md` — Fluxo de commit e push
