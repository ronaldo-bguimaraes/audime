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
- Testes com SQLite exigem `schema_translate_map` e `with_variant` para `BigInteger`

## Ciclo 2 — Autenticação sem senha

### O que funcionou
- Arquitetura de `EmailSender` abstrato com `LogEmailSender` permite trocar implementação sem mexer no fluxo
- `PyJWT` com HS256 é simples e direto para MVP
- Rate limiting básico com `AuthCode.attempts` + cooldown de 60s

### O que aprendemos
- Testes com SQLite exigem `schema_translate_map` para ignorar schemas PostgreSQL (`core`, `raw`, etc.)
- `sa.BigInteger` não auto-incrementa no SQLite — usar `with_variant(sa.Integer(), "sqlite")`
- `DateTime(timezone=True)` no SQLite perde timezone — `expires_at.replace(tzinfo=...)` ao comparar
- `HTTPBearer` do FastAPI retorna 401 (não 403) quando token está ausente
- `get_current_user_id()` agora lê do JWT via `Depends(security)` — endpoints protegidos por padrão

### Pendências
- Trocar `LogEmailSender` por SMTP real (Resend, SendGrid, Gmail)
- Adicionar refresh token + rotação
- Adicionar Redis para rate limiting em produção
- Migrar tabela `auth_code` para SQL de produção em `scripts.sql`
