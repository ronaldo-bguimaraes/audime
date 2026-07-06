# Fluxo de Sprint — Squad Agent System

> Processo completo de sprint orquestrado pelo **scrum_master**.
> Cada sprint segue TDD estrito: especificação → descoberta → teste → implementação → validação → arquivamento.

## Visão Geral

```
Refinement → Discovery → Test Spec → Development → Validation → Review & Archive
    1            2              3             4              5              6
```

Cada passo é executado por um agente especializado. O scrum_master coordena e garante que
as regras (spec-first, TDD-first, audit mandatory, maker-checker split) sejam seguidas.

---

## Step 1: Refinement

**Ator:** `product_owner` (modo refinement)
**Artefato:** `.agents/workspace/specification.md`

1. O scrum_master ativa o **product_owner** em modo refinement
2. O product_owner lê o estado atual (`lessons.md`, `docs/`)
3. Define **critérios binários verificáveis** — cada critério deve incluir:
   - Comportamento esperado observável
   - Como será testado (comando, assertion, resultado observável)
4. Escreve `.agents/workspace/specification.md` com formato padronizado
5. **Regra:** Se não houver critérios, o sprint não começa
6. **Regra:** Todo critério deve ser traduzível em um teste determinístico

### Formato da Specification

```markdown
# Specification — Nome do Sprint

## Acceptance Criteria
- [ ] **Descrição**: evidência esperada
      **Test**: como será verificado (ex: `pytest tests/test_X.py::test_Y`)
```

---

## Step 2: Discovery & Plan

**Atores:** `product_manager` + `tech_lead` (paralelo)
**Artefatos:** `.agents/workspace/hypotheses.md`, `.agents/workspace/plan.md`

O scrum_master ativa em paralelo:
- **product_manager** — questiona as premissas, pesquisa alternativas, desafia decisões
- **tech_lead** — esclarece conceitos técnicos, avalia arquitetura

Após pesquisa:
1. Consolidar resultados
2. Registrar hipóteses em `.agents/workspace/hypotheses.md`
3. Criar plano em `.agents/workspace/plan.md`
4. Opcional: ativar **developer** para registrar conhecimento em `.agents/state/knowledge/`

---

## Step 3: Test Specification

**Ator:** `developer` (modo test-spec)
**Artefatos:** `tests/`, `.agents/workspace/test-manifest.md`

1. O developer escreve **testes que falham** em `tests/` — cada critério da specification
   mapeia para ao menos um teste
2. **Regra:** Nenhuma implementação sem um teste falhando que a defina
3. Confirmar que os testes falham contra o código atual (prova que testam comportamento real)
4. Registrar arquivos de teste criados/alterados em `.agents/workspace/test-manifest.md`

---

## Step 4: Development

**Ator:** `developer` (modo implement)
**Artefato:** Código-fonte modificado

1. O developer modifica a implementação **apenas** para satisfazer os testes
2. **Re-executar os testes antes de qualquer commit**
3. Antes de cada commit, ativar `devops_engineer` para varredura de credenciais
4. **Regra:** Commits seguem o formato `tipo(escopo): descrição` (≤50 caracteres, imperativo)
5. **Regra:** Se um teste falhar, isolar a mudança mínima para corrigi-lo — não expandir escopo
6. **Regra:** Adaptar a implementação aos testes, nunca os testes à implementação

### Convenção de Commits

Ver `docs/commit-flow.md` e `.agents/workspace/commit_conventions.md`.

---

## Step 5: Validation & Improvement

**Atores:** `qa_engineer` + `devops_engineer`
**Artefatos:** `.agents/workspace/validation.md`

1. O scrum_master lê `lessons.md`
2. Ativa **qa_engineer** para:
   - Executar **regressão completa** (todos os testes relacionados, não só os novos)
   - Verificar critérios de `.agents/workspace/specification.md`
   - Confirmar que nenhum comportamento existente foi quebrado
3. Ativa **devops_engineer** para auditoria de segurança final
4. Registra resultado em `.agents/workspace/validation.md`

### Se falhar:
1. Ativar **product_manager** para investigar
2. Registrar em `.agents/state/lessons.md`
3. Retornar ao Step 2

### Se passar:
1. Ativar **tech_lead** para code review
2. Refatorar se necessário
3. Re-validar

---

## Step 6: Review & Archive

**Ator:** `product_owner` (modo review)
**Artefatos:** `.agents/state/records/`

1. Ativar **product_owner** em modo review para auditar `.agents/workspace/specification.md`
2. Verificar cada critério contra evidência real
3. Atualizar specification.md com resultado (✅ ou ❌)

### Se falhou:
- Registrar em `lessons.md`
- Retornar ao Step 2

### Se passou:
1. Product_owner arquiva sumário em `.agents/state/records/`
2. **Loop guard:** Se o arquivo mais recente tiver o mesmo sumário do anterior, parar e alertar
3. Informar o que foi feito e quais critérios foram atendidos
4. Perguntar: "Deseja iniciar o próximo sprint?"

---

## Discovery Mode

Modo leve para responder perguntas sem acionar o ciclo completo.

1. **Contexto:** ler `lessons.md`, `records/`, `docs/`
2. **Pesquisa:** ativar `product_manager` + `tech_lead` em paralelo
3. **Resposta:** consolidar e responder diretamente ao usuário
4. **Opcional:** registrar em `lessons.md` (com `#discovery`) ou em `.agents/workspace/analysis.md`

### Regras do Discovery Mode
- Apenas pesquisar e responder — não implementar, não commitar, não validar
- Não alterar `specification.md`, `validation.md`, `plan.md`, `hypotheses.md`
- Não alterar `.agents/state/records/`, `.gitignore`, `.agents/agents/`
- Se a pergunta evoluir para "implementar", migrar para o ciclo completo

---

## Regras Core

| Regra | Descrição |
|-------|-----------|
| Spec-first | Nenhum sprint sem `.agents/workspace/specification.md` |
| TDD-first | Nenhuma implementação sem um teste falhando |
| Audit mandatory | Nenhum sprint termina sem validação do product_owner |
| Maker-checker split | product_owner ≠ implementador ≠ qa_engineer |
| No-downgrade | Toda iteração melhora o projeto em ao menos um aspecto |
| Passing tests > existing | Implementação se adapta aos testes, nunca o inverso |
| Regression mandatory | Toda mudança re-executa todos os testes relacionados |
| Security first | Antes de todo commit: `@devops_engineer` para scan de credenciais |
| Loop guard | Dois ciclos consecutivos com o mesmo resultado = alerta |
| Improvement not optional | Refatorar antes de arquivar |

---

## Ver Também

- `docs/github-cli-workflow.md` — Criar issues e gerenciar project boards
- `docs/commit-flow.md` — Fluxo de commit e push com segurança
- `.agents/agents/scrum_master.md` — Definição canônica do scrum_master
- `.agents/agents/product_owner.md` — Definição do product_owner
- `.agents/agents/developer.md` — Definição do developer
- `.agents/agents/qa_engineer.md` — Definição do qa_engineer
- `.agents/agents/devops_engineer.md` — Definição do devops_engineer
- `.agents/agents/product_manager.md` — Definição do product_manager
- `.agents/agents/tech_lead.md` — Definição do tech_lead
