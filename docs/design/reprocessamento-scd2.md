# Plan — Reprocessamento Analítico com SCD Type 2

> **Status**: Rascunho para validação
> **Data**: 2026-07-05

---

## 1. Arquitetura Geral

```
┌─ Frontend Preview ─────────────────────────────────────────────────┐
│  Lista extrações → expande → vê histórico RAW (append, versões)    │
└─────────────────────────────────────────────────────────────────────┘
        ▲
        │ GET /v1/extracoes (inclui raw historico)
        │
┌───────┴──────────┐    ┌─────────────────┐    ┌──────────────────────┐
│   RAW (append)   │───▶│   STAGING (dedup) │───▶│  ANALYTICS (SCD2)    │
│  raw.nota        │    │  staging.nota    │    │  analytics.nota      │
│  raw.item_nota   │    │  staging.item    │    │  analytics.item      │
│  raw.importacao  │    │                  │    │  + valid_from        │
│  (já append-only)│    │                  │    │  + valid_to          │
└──────────────────┘    └──────────────────┘    │  + is_current        │
        │                                       │  + version           │
        │                                       └──────────┬───────────┘
        │                                                  │
        │                                                  ▼
        │                                       ┌──────────────────┐
        │                                       │  Frontend Final  │
        │                                       │  Dashboard       │
        │                                       │  (is_current)    │
        │                                       └──────────────────┘
        │
        │ Evento: ARQ job "transformar_extracao"
        ▼
┌──────────────────┐
│  Transform       │
│  Pipeline        │
│  raw→staging→ana │
└──────────────────┘
```

### Fluxo de reprocessamento

1. Usuário aciona `POST /v1/extracoes/{id}/reprocessar`
2. Endpoint valida (status DONE/ERROR, ownership), seta `status=PENDING`, enfileira ARJOB
3. **Worker** executa `executar_extracao(id_extracao, ..., reprocess=True)`:
   a. Download HTML + upload R2
   b. Cria `raw.importacao` (append — já é assim)
   c. Parseia HTML → `NotaExtraida`
   d. **INSERT** em `raw.nota` + `raw.item_nota` (sempre nova linha, sem UPDATE)
   e. Publica evento: enfileira `transformar_extracao(id_extracao, id_nota, id_importacao)`
   f. Seta `status=DONE`
4. **Transform pipeline** (worker separado ou no mesmo pool):
   a. Lê `raw.nota`, `raw.item_nota`, `raw.importacao`
   b. Normaliza → `staging.nota_normalizada`, `staging.item_normalizado`
   c. SCD2 no analytics:
      - Marca versão anterior como `is_current=false, valid_to=now()`
      - Insere nova versão com `is_current=true, valid_from=now(), version=N+1`

---

## 2. Modelagem de Dados

### 2.1 RAW — Append-only

Sem UNIQUE constraint de negócio. Sem UPDATE. Sem DELETE. Cada parsing é um INSERT novo.

```sql
-- raw.nota (já existe, sem mudanças estruturais)
-- Mas muda o uso: não usa mais UNIQUE(chave, id_usuario) como barreira
-- Reprocessamento sempre gera NOVA linha

-- raw.item_nota (já existe)
-- FK id_nota aponta pra raw.nota sempre

-- raw.importacao (já existe, já append-only)
-- Cada tentativa de parsing gera uma nova linha
```

**Mudanças necessárias no raw:**
- `raw.importacao.id_extracao` não é UNIQUE — várias importações por extração (já deve ser assim, verificar)

### 2.2 STAGING — Normalização e dedup

```sql
CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE staging.nota_normalizada (
    id_nota_normalizada BIGSERIAL PRIMARY KEY,
    id_nota BIGINT NOT NULL REFERENCES raw.nota(id_nota),
    id_importacao BIGINT NOT NULL REFERENCES raw.importacao(id_importacao),
    id_extracao BIGINT NOT NULL REFERENCES core.extracao(id_extracao),
    id_usuario BIGINT NOT NULL REFERENCES core.usuario(id_usuario),
    chave_acesso VARCHAR(44),
    empresa VARCHAR(255),
    numero VARCHAR(20),
    serie VARCHAR(10),
    emissao DATE,
    valor_total NUMERIC(12,2),
    qtd_total_itens INTEGER,
    extra JSONB,
    processado_em TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Uma importação gera uma normalização
    UNIQUE(id_importacao)
);

CREATE TABLE staging.item_normalizado (
    id_item_normalizado BIGSERIAL PRIMARY KEY,
    id_nota_normalizada BIGINT NOT NULL REFERENCES staging.nota_normalizada(id_nota_normalizada),
    id_item_nota BIGINT REFERENCES raw.item_nota(id_item_nota),
    id_usuario BIGINT NOT NULL REFERENCES core.usuario(id_usuario),
    descricao VARCHAR(255),
    quantidade NUMERIC(12,3),
    unidade VARCHAR(10),
    valor_unitario NUMERIC(12,2),
    valor_total NUMERIC(12,2),
    processado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Índice para lookup por extração
CREATE INDEX idx_staging_nota_extracao ON staging.nota_normalizada(id_extracao);
```

**Relacionamento:** staging reflete 1:1 com raw — cada `importacao` vira uma `nota_normalizada`. Staging é a versão "limpa" dos dados crus.

### 2.3 ANALYTICS — SCD Type 2

```sql
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE analytics.nota (
    id_nota_analytics BIGSERIAL PRIMARY KEY,
    id_extracao BIGINT NOT NULL,  -- business key para SCD2
    id_usuario BIGINT NOT NULL,
    chave_acesso VARCHAR(44),
    empresa VARCHAR(255),
    numero VARCHAR(20),
    serie VARCHAR(10),
    emissao DATE,
    valor_total NUMERIC(12,2),
    qtd_total_itens INTEGER,
    extra JSONB,

    -- SCD Type 2 columns
    version INTEGER NOT NULL DEFAULT 1,
    valid_from TIMESTAMPTZ NOT NULL DEFAULT now(),
    valid_to TIMESTAMPTZ,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,

    -- Metadados de linhagem
    id_importacao BIGINT,
    id_nota_raw BIGINT,
    processado_em TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_analytics_nota_current UNIQUE (id_extracao, is_current)
    -- Só UM registro current por extração
    -- (partial index no PostgreSQL, mas UNIQUE com filtro não é padrão SQL)
);

-- Partial unique index: só um current por extração
CREATE UNIQUE INDEX uq_analytics_nota_current
    ON analytics.nota(id_extracao) WHERE is_current = TRUE;

CREATE TABLE analytics.item_nota (
    id_item_analytics BIGSERIAL PRIMARY KEY,
    id_nota_analytics BIGINT NOT NULL REFERENCES analytics.nota(id_nota_analytics),
    descricao VARCHAR(255),
    quantidade NUMERIC(12,3),
    unidade VARCHAR(10),
    valor_unitario NUMERIC(12,2),
    valor_total NUMERIC(12,2),

    -- SCD2: versão herdada da nota pai
    version INTEGER NOT NULL,
    processado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_analytics_item_nota ON analytics.item_nota(id_nota_analytics);
```

**Regra SCD2:** Quando uma nova versão da mesma extração chega:

```sql
BEGIN;
-- 1. Fechar versão anterior
UPDATE analytics.nota
SET valid_to = now(), is_current = FALSE
WHERE id_extracao = $id_extracao AND is_current = TRUE;

-- 2. Inserir nova versão
INSERT INTO analytics.nota (...)
VALUES (..., version = (SELECT COALESCE(MAX(version), 0) + 1 FROM analytics.nota WHERE id_extracao = $id_extracao), ...);

-- 3. Inserir novos itens
INSERT INTO analytics.item_nota (...)
SELECT ...;
COMMIT;
```

---

## 3. API Changes

### 3.1 `POST /v1/extracoes/{id}/reprocessar`

```json
// Request (opcional)
{ "url": "https://..." }

// Response 202
{
  "id_extracao": 42,
  "status": "PENDING",
  "job_id": "extracao:42:reprocess:1"
}
```

**Validações:**
| Condição | Response |
|----------|----------|
| Extração não existe ou outro usuário | 404 |
| Status PENDING ou RUNNING | 409 |
| URL ausente e extracao.url é null | 422 |
| Tudo OK | 202 + enfileira ARJOB |

### 3.2 `GET /v1/extracoes` — Preview com histórico RAW

Response atual inclui `status` da extração. Adicionar array `historico_parsing`:

```json
{
  "id_extracao": 42,
  "status": "DONE",
  "url": "...",
  "created_at": "...",
  "reprocess_count": 2,
  "reprocessed_at": "...",
  "historico_parsing": [
    {
      "id_importacao": 1,
      "id_nota": 10,
      "imported_at": "2026-07-05T10:00:00Z",
      "empresa": "SUPERMERCADOS BH",
      "chave": "3125...",
      "numero": "382376",
      "serie": "69",
      "emissao": "2025-10-07",
      "valor_total": 273.87,
      "qtd_total_itens": 11,
      "items": [
        { "descricao": "SUCO ALIANCA 1L", "quantidade": 9.0, "unidade": "TP", "valor_total": 107.10 }
      ]
    },
    {
      "id_importacao": 2,
      "id_nota": 42,
      "imported_at": "2026-07-06T15:00:00Z",
      ...
    }
  ]
}
```

O frontend existente continua funcionando (mesmos campos), mas agora ganha um acordeão/expansão pra ver as versões anteriores.

### 3.3 `GET /v1/dashboard/notas` — Novo endpoint para exibição final

Lê do `analytics.nota WHERE is_current = TRUE`:

```json
{
  "notas": [
    {
      "id_nota_analytics": 1,
      "id_extracao": 42,
      "empresa": "...",
      "chave": "...",
      "numero": "...",
      "serie": "...",
      "valor_total": 273.87,
      "qtd_total_itens": 11,
      "items": [
        { "descricao": "...", "quantidade": 9.0, "unidade": "TP", "valor_total": 107.10 }
      ],
      "version": 2,
      "valid_from": "2026-07-06T15:00:00Z"
    }
  ]
}
```

### 3.4 `GET /v1/dashboard/notas/{id}/historico` — Histórico de versões

Retorna todas as versões SCD2 de uma nota:

```json
{
  "versoes": [
    { "version": 1, "valid_from": "...", "valid_to": "2026-07-06T15:00:00Z", "valor_total": 166.77, ... },
    { "version": 2, "valid_from": "2026-07-06T15:00:00Z", "valid_to": null, "is_current": true, "valor_total": 273.87, ... }
  ]
}
```

---

## 4. Pipeline de Transform (Evento)

### 4.1 Evento

Worker, após inserir no raw, enfileira:

```python
await pool.enqueue_job(
    'app.workers.tasks.transformar_extracao',
    id_extracao=42,
    _queue_name='audime:transform',
)
```

### 4.2 Worker de transform

```python
async def transformar_extracao(ctx, *, id_extracao: int):
    """Pipeline raw → staging → analytics SCD2."""

    # 1. Busca última importação da extração
    importacao = db.query(Importacao).filter(
        Importacao.id_extracao == id_extracao
    ).order_by(Importacao.imported_at.desc()).first()

    nota_raw = db.query(Nota).filter(
        Nota.id_importacao == importacao.id_importacao
    ).first()

    # 2. Upsert no staging (normaliza)
    staging_nota = normalizar_nota(db, nota_raw, importacao)

    # 3. SCD2 no analytics
    # Fecha versão anterior
    db.query(AnalyticsNota).filter(
        AnalyticsNota.id_extracao == id_extracao,
        AnalyticsNota.is_current == True
    ).update({"valid_to": now(), "is_current": False})

    # Insere nova versão
    nova_versao = AnalyticsNota(
        id_extracao=id_extracao,
        id_usuario=nota_raw.id_usuario,
        chave_acesso=nota_raw.chave,
        empresa=nota_raw.empresa,
        # ... demais campos ...
        version=db.query(func.max(AnalyticsNota.version)).filter(
            AnalyticsNota.id_extracao == id_extracao
        ).scalar() or 0 + 1,
        valid_from=now(),
        is_current=True,
        id_importacao=importacao.id_importacao,
        id_nota_raw=nota_raw.id_nota,
    )
    db.add(nova_versao)
    db.flush()

    # Itens
    for item_raw in nota_raw.items:
        db.add(AnalyticsItemNota(
            id_nota_analytics=nova_versao.id_nota_analytics,
            descricao=item_raw.item_descricao,
            quantidade=item_raw.item_quantidade,
            unidade=item_raw.item_tipo_unidade,
            valor_unitario=item_raw.item_valor_unidade,
            valor_total=item_raw.item_valor_total,
            version=nova_versao.version,
        ))

    db.commit()
```

### 4.3 Fila separada

ARQ worker precisa de uma segunda fila:

```python
# app/workers/arq_settings.py
class WorkerSettings:
    functions = [
        "app.workers.tasks.executar_extracao",
        "app.workers.tasks.transformar_extracao",
    ]
    queue_name = "audime:extracoes"  # fila padrão

# Job de transform usa fila específica
await pool.enqueue_job(
    'transformar_extracao',
    id_extracao=...,
    _queue_name='audime:transform',
)
```

Ou pode usar a mesma fila — o namespace já separa por nome da função.

---

## 5. Frontend

### 5.1 Preview (já existe, adaptar)

- `GET /v1/extracoes` agora retorna `historico_parsing` (array)
- Na lista, cada extração tem um botão/ícone de expansão
- Expandido: tabela com todas as tentativas de parsing, ordenadas por data decrescente
- Cada linha mostra: data, empresa, valor, status do parsing

### 5.2 Dashboard (novo)

- Novo endpoint `GET /v1/dashboard/notas` → analytics SCD2
- Tabela de notas com dados consolidados (sempre a versão atual)
- Cada nota tem link pra ver histórico SCD2 (`GET /v1/dashboard/notas/{id}/historico`)

---

## 6. Migrations

### Migration 1: `analytics` schema + tabelas SCD2

- Cria schema `analytics` se não existir
- Cria `analytics.nota` com SCD2 columns
- Cria `analytics.item_nota`
- Cria partial unique index

### Migration 2: `staging` schema + tabelas

- Cria schema `staging` se não existir
- Cria `staging.nota_normalizada` com UNIQUE(id_importacao)
- Cria `staging.item_normalizado` com FK pra staging.nota_normalizada

### Migration 3: `reprocess_count` + `reprocessed_at` em `core.extracao`

(Já planejado no plano anterior — mantém)

### Migration 4: Remover UNIQUE constraint de raw (opcional)

Discussão: manter ou remover `UNIQUE(chave, id_usuario)`?

- **Manter**: ainda protege contra duplicatas acidentais em extrações normais (primeira tentativa). Se reprocess, o chave pode ser igual e o INSERT vai falhar — mas o worker usa savepoint pra tratar.
- **Remover**: raw é append-only estrito, sem constraints de negócio.

**Recomendação**: **Manter** a constraint, mas o worker trata `IntegrityError` com savepoint (fallback pra INSERT com chave alternativa ou log de erro). A constraint ainda é útil como rede de segurança pra extrações normais.

---

## 7. Tratamento de Chave Duplicada no Worker (Append-only)

Mesmo com raw append-only, a `UNIQUE(chave, id_usuario)` existe. Quando o reprocessamento produz a mesma chave:

```python
try:
    with db.begin_nested():  # savepoint
        nota = Nota(..., chave=chave, id_usuario=id_usuario)
        db.add(nota)
        db.flush()
except IntegrityError:
    # Chave já existe — em modo append-only, isso não deveria acontecer
    # Mas se acontecer (ex: chave não mudou entre parsings):
    # Log aviso, mas ainda assim insere (como fazer?)
    # Opção A: Permitir chave duplicada removendo a constraint
    # Opção B: Adicionar um suffix/timestamp na chave (feio)
    # Opção C: Usar savepoint e gerar chave = chave + f"-v{version}"
    pass
```

**Proposta**: Remover `UNIQUE(chave, id_usuario)` do raw. A constraint de unicidade passa a ser responsabilidade do analytics (`UNIQUE(id_extracao, is_current)`). O raw não precisa dessa constraint porque ele é só um log de ingestão.

Se o usuário concordar, a migration 4 remove a constraint.

---

## 8. Implementação (Steps)

| Step | Descrição | Arquivos | Prio |
|------|-----------|----------|------|
| 1 | Criar schemas `staging` + `analytics` + migrations | `alembic/versions/` | P0 |
| 2 | Adicionar `reprocess_count`, `reprocessed_at` no `core.extracao` | `abstract/models/core.py`, migration | P1 |
| 3 | Schemas Pydantic: `ReprocessarExtracaoRequest`, response com `historico_parsing` | `app/api/v1/schemas.py` | P0 |
| 4 | Endpoint `POST /v1/extracoes/{id}/reprocessar` | `app/api/v1/endpoints/extracoes.py` | P0 |
| 5 | Worker: append-only insert, publicar evento transform | `app/workers/tasks.py` | P0 |
| 6 | Pipeline de transform: raw → staging → analytics SCD2 | `app/workers/transform_pipeline.py` | P0 |
| 7 | Endpoint `GET /v1/dashboard/notas` (analytics current) | `app/api/v1/endpoints/dashboard.py` (novo) | P1 |
| 8 | Frontend: expansão de histórico raw no preview | `web/src/pages/Extrair.tsx` | P1 |
| 9 | Frontend: dashboard lendo do analytics | `web/src/pages/Dashboard.tsx` | P1 |
| 10 | Testes | `tests/` | P2 |
| 11 | Remover UNIQUE constraint raw (se aprovado) | `alembic/versions/` | P2 |

### Dependências

```
Step 1 ──────▶ Step 3 ──▶ Step 4 ──▶ Step 5 ──▶ Step 6 ──▶ Step 7
                                                              │
Step 2 ──────▶ Step 3 ──▶ Step 4                             │
                                                              ▼
                                                         Steps 8-9
                                                              │
                                                              ▼
                                                         Step 10-11
```

---

## 9. Testes

### 9.1 Testes de Unidade

| Teste | O que verifica |
|-------|---------------|
| Worker faz INSERT (não UPDATE) em reprocess | `raw.nota` tem 2 linhas pra mesma extração |
| Transform pipeline SCD2 | Analytics tem 2 versões, `is_current` correto |
| GET dashboard retorna só current | Filtro `is_current=true` funciona |
| GET extracoes retorna histórico raw | `historico_parsing` array com todas tentativas |
| POST reprocessar com status errado | 409 pra PENDING/RUNNING |
| Chave duplicada no raw (sem constraint) | INSERT funciona sem erro |
| Evento encadeado | Worker enfileira transform após parser |

### 9.2 Testes de Regressão

- Preview atual continua funcionando (mesmos campos, só ganha `historico_parsing`)
- Autenticação não quebrada
- Extração normal (não reprocess) continua igual

---

## 10. Riscos e Mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Staging + analytics aumenta latência do parsing | Usuário espera mais pra ver resultado | Pipeline é async (fila separada). Preview do raw fica disponível imediatamente. Analytics eventualmente consistente. |
| SCD2 cresce sem limite | Tabela grande com versões antigas | Definir política de retenção futura (ex: manter últimas N versões). Não implementar agora. |
| Erro no transform pipeline | Analytics desatualizado | Logging + retry do ARQ job. Se falhar, reprocess manual. |
| Concorrência: dois reprocess simultâneos | Ordem errada de versões | Row lock na extração (`with_for_update`). Transform processa sequencialmente por `id_extracao`. |
| Remover UNIQUE do raw causa duplicata silenciosa | Raw tem linhas duplicadas | Raw é log — duplicata é aceitável. Analytics faz dedup por `id_extracao + is_current`. |

---

## 11. Decisões Finais (validadas)

- [x] **Remover `UNIQUE(chave, id_usuario)` do raw** — raw é log puro, sem constraints de negócio.
- [x] **Fila de transform separada** — `audime:transform` para o pipeline raw→staging→analytics.
- [x] **Preview histórico raw**: últimas 10 versões no expandable inline; clicar abre tela separada com detalhes completos.
- [x] **Dashboard substitui listagem atual** — passa a ser baseado no analytics (`is_current=true`).
