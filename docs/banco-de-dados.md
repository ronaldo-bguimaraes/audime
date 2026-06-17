# Banco de Dados

## Stack

- PostgreSQL (Supabase)
- ORM: SQLAlchemy (Python)

## Schemas

| Schema | Finalidade |
|---|---|
| `raw` | Dados brutos importados (imutáveis, fonte original) |
| `core` | Entidades principais do sistema (extração, usuário) |
| `staging` | (futuro) Dados intermediários — limpeza, tipagem, normalização |
| `analytics` | (futuro) Agregações e métricas para análise |

## Regras

- Todo dado entra primeiro em `raw`
- Processamento e normalização ocorrem em `staging`
- Entidades finais ficam em `core`
- Agregações e métricas ficam em `analytics`
- Tudo deve ser rastreável por `id_usuario`
- Importações são rastreadas via `core.extracao` e `raw.importacao`
- Arquivos ficam no Cloudflare R2, nunca no banco
- Banco armazena apenas metadados + referências para o R2

---

## ENUMs

```sql
CREATE TYPE core.extracao_status AS ENUM (
    'PENDING', 'RUNNING', 'DONE', 'ERROR'
);
```

---

## Tabelas

### core.usuario

| Coluna | Tipo | Restrições |
|---|---|---|
| id_usuario | BIGINT | PK, GENERATED ALWAYS AS IDENTITY |
| nome | TEXT | NOT NULL |
| email | TEXT | NOT NULL, UNIQUE |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| updated_at | TIMESTAMPTZ | DEFAULT now() |

### core.extracao

| Coluna | Tipo | Restrições |
|---|---|---|
| id_extracao | BIGINT | PK, GENERATED ALWAYS AS IDENTITY |
| status | core.extracao_status | NOT NULL, DEFAULT 'PENDING' |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() |
| id_usuario | BIGINT | FK → core.usuario(id_usuario) |

### raw.importacao

| Coluna | Tipo | Restrições |
|---|---|---|
| id_importacao | BIGINT | PK, GENERATED ALWAYS AS IDENTITY |
| storage_bucket | VARCHAR(63) | NOT NULL |
| storage_key | TEXT | NOT NULL |
| storage_filename | TEXT | NOT NULL |
| sha256 | CHAR(64) | NOT NULL |
| imported_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() |
| id_extracao | BIGINT | FK → core.extracao(id_extracao) |
| id_usuario | BIGINT | NOT NULL, FK → core.usuario(id_usuario) |

### raw.fatura

| Coluna | Tipo | Restrições |
|---|---|---|
| id_fatura | BIGINT | PK, GENERATED ALWAYS AS IDENTITY |
| banco | VARCHAR(50) | NOT NULL |
| nome_titular | TEXT | NOT NULL |
| mes_referencia | DATE | |
| extra | JSONB | DEFAULT '{}' |
| imported_at | TIMESTAMPTZ | DEFAULT now() |
| id_usuario | BIGINT | NOT NULL, FK → core.usuario(id_usuario) |
| id_importacao | BIGINT | FK → raw.importacao(id_importacao) |

### raw.transacao

| Coluna | Tipo | Restrições |
|---|---|---|
| id_transacao | BIGINT | PK, GENERATED ALWAYS AS IDENTITY |
| data_realizacao | DATE | NOT NULL |
| descricao | TEXT | |
| valor | NUMERIC(8,2) | NOT NULL |
| final_cartao | CHAR(4) | |
| parcela | TEXT | |
| extra | JSONB | DEFAULT '{}' |
| imported_at | TIMESTAMPTZ | DEFAULT now() |
| id_fatura | BIGINT | FK → raw.fatura(id_fatura) |
| id_importacao | BIGINT | FK → raw.importacao(id_importacao) |
| id_usuario | BIGINT | NOT NULL, FK → core.usuario(id_usuario) |

### raw.nota

| Coluna | Tipo | Restrições |
|---|---|---|
| id_nota | BIGINT | PK, GENERATED ALWAYS AS IDENTITY |
| empresa | TEXT | NOT NULL |
| chave | CHAR(44) | NOT NULL, UNIQUE |
| numero | TEXT | NOT NULL |
| serie | TEXT | NOT NULL |
| emissao | DATE | NOT NULL |
| valor_total | NUMERIC(10,2) | NOT NULL |
| extra | JSONB | DEFAULT '{}' |
| imported_at | TIMESTAMPTZ | DEFAULT now() |
| id_usuario | BIGINT | NOT NULL, FK → core.usuario(id_usuario) |
| id_fatura | BIGINT | FK → raw.fatura(id_fatura) |
| id_importacao | BIGINT | FK → raw.importacao(id_importacao) |

### raw.item_nota

| Coluna | Tipo | Restrições |
|---|---|---|
| id_item_nota | BIGINT | PK, GENERATED ALWAYS AS IDENTITY |
| item_codigo | TEXT | |
| item_descricao | TEXT | NOT NULL |
| item_quantidade | NUMERIC(10,3) | NOT NULL, DEFAULT 1 |
| item_tipo_unidade | TEXT | DEFAULT 'UN' |
| item_valor_unidade | NUMERIC(10,2) | NOT NULL |
| item_valor_total | NUMERIC(10,2) | NOT NULL |
| extra | JSONB | DEFAULT '{}' |
| imported_at | TIMESTAMPTZ | DEFAULT now() |
| id_nota | BIGINT | NOT NULL, FK → raw.nota(id_nota) |
| id_usuario | BIGINT | NOT NULL, FK → core.usuario(id_usuario) |

### staging (futuro)

Tabelas planejadas:

- `staging.nota_normalizada` — Cópia limpa e tipada de `raw.nota`
- `staging.item_normalizado` — Cópia limpa e tipada de `raw.item_nota`

### analytics (futuro)

Tabelas planejadas:

- `analytics.gasto_mensal` — Agregação mensal por usuário (total gasto, qtd transações, qtd notas)
- `analytics.gasto_categoria` — Agregação por categoria (total gasto, qtd itens)

---

## Relacionamentos

```
core.usuario
├── core.extracao       (1:N)
├── raw.importacao      (1:N)
├── raw.fatura          (1:N)
├── raw.transacao       (1:N)
├── raw.nota            (1:N)
└── raw.item_nota       (1:N)

core.extracao
└── raw.importacao      (1:N)

raw.importacao
├── raw.fatura          (1:N)
├── raw.transacao       (1:N)
└── raw.nota            (1:N)

raw.fatura
├── raw.transacao       (1:N)
└── raw.nota            (1:N)

raw.nota
└── raw.item_nota       (1:N)
```

---

## Índices (implementação futura)

Criar quando houver degradação de performance nas queries mais comuns:

```sql
CREATE INDEX idx_extracao_usuario    ON core.extracao(id_usuario);
CREATE INDEX idx_importacao_usuario  ON raw.importacao(id_usuario);
CREATE INDEX idx_importacao_extracao ON raw.importacao(id_extracao);
CREATE INDEX idx_fatura_usuario      ON raw.fatura(id_usuario);
CREATE INDEX idx_transacao_usuario   ON raw.transacao(id_usuario);
CREATE INDEX idx_transacao_fatura    ON raw.transacao(id_fatura);
CREATE INDEX idx_nota_usuario        ON raw.nota(id_usuario);
CREATE INDEX idx_nota_fatura         ON raw.nota(id_fatura);
CREATE INDEX idx_nota_chave          ON raw.nota(chave);
CREATE INDEX idx_item_nota           ON raw.item_nota(id_nota);
CREATE INDEX idx_item_nota_usuario   ON raw.item_nota(id_usuario);
```

---

## Notas de Migração

1. `raw.importacao` deve referenciar `core.extracao` — criar `core.extracao` **antes** de `raw.importacao`
2. `raw.fatura` sem `id_importacao` por enquanto (backfill opcional)
3. `raw.transacao` sem `imported_at` no schema atual — adicionar na próxima migração
4. `sha256` como `TEXT` no schema atual — migrar para `CHAR(64)`
