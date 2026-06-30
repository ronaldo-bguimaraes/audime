# Lições Aprendidas

<!-- Acumuladas entre ciclos. Toda falha vira lição aqui. -->

## Ciclo 1 — Segurança + Correção de Imports

### O que funcionou
- A varredura de histórico com `git log -p | grep` é suficiente para projetos pequenos — não precisa de gitleaks/trufflehog
- `rg` é eficaz para encontrar referências residuais após rename de pacote
- `pydantic-settings` com `extra="ignore"` evita falhas por vars extras no `.env`

### O que aprendemos
- O pacote `database` foi renomeado para `abstract` mas os imports não foram atualizados — 8 arquivos quebrados
- `sa.JSONB` não existe no SQLAlchemy 2.0+ — usar `sa.JSON`
- O `.env` sempre esteve no `.gitignore` e nunca foi commitado — boa prática desde o início
- `.env.example` continha `R2_TOKEN` que não é usado pelo `Settings` — foi removido para clareza

### Riscos identificados
- `abstract.engine` importa `app.core.config` — dependência entre pacotes irmãos. Se `app.core.config` um dia importar algo de `abstract`, forma circular import
- Parser NFC-e continua frágil (seletores hardcoded para MT)
- Extração síncrona na request (bloqueia FastAPI)
- Zero testes reais (só placeholder)
