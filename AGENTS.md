# Audime — Loopback

Este diretório contém o agente loopback para desenvolvimento incremental.

## Estrutura

```
.agents/
  agents/         ← Definições dos agentes (loopback, questionador, etc.)
  policies/       ← Políticas de segurança
  workspace/      ← Artefatos do ciclo (spec, validação, plano)
  state/          ← Estado persistente (lessons.md) e transitório (memoria/)
AGENTS.md         ← Entry point para o agente
```

## Uso

O agente loopback coordena ciclos de 5 passos:
1. **Spec** — define critérios em `.agents/workspace/spec.md`
2. **Questionamento** — pesquisa e desafia com questionador + explicador
3. **Desenvolvimento** — implementa
4. **Validação** — verifica critérios
5. **Arquivo** — registra em `.agents/state/memoria/`

Para consultas rápidas sem alterar arquivos, use o **Modo Análise**.

## Regras

- Spec-first: nenhum ciclo sem critérios
- Audit mandatory: nenhum ciclo termina sem validação
- Maker-checker split: especulador ≠ implementador ≠ validador
- No-downgrade: toda iteração melhora o projeto
- **Segurança first**: antes de todo `git commit` ou `git push`, execute `@seguranca` para varrer credenciais vazadas. Se o seguranca apontar issues, resolva antes de prosseguir.
