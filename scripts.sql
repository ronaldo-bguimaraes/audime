-- Schema: Audime
-- Database: PostgreSQL

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS analytics;

-- ============================================================
-- ENUMS
-- ============================================================

CREATE TYPE core.extracao_status AS ENUM (
    'PENDING',
    'RUNNING',
    'DONE',
    'ERROR'
);

-- ============================================================
-- CORE
-- ============================================================

CREATE TABLE core.usuario (
    id_usuario BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome       TEXT NOT NULL,
    email      TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE core.auth_code (
    id_auth_code    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email           TEXT NOT NULL,
    code_hash       CHAR(64) NOT NULL,
    expires_at      TIMESTAMPTZ NOT NULL,
    used            BOOLEAN DEFAULT FALSE,
    attempts        INTEGER DEFAULT 0,
    last_attempt_at TIMESTAMPTZ
);

CREATE INDEX idx_auth_code_email ON core.auth_code(email);

CREATE TABLE core.extracao (
    id_extracao BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    status      core.extracao_status NOT NULL DEFAULT 'PENDING',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    id_usuario  BIGINT NOT NULL REFERENCES core.usuario(id_usuario)
);

-- ============================================================
-- RAW — Dados brutos importados
-- ============================================================

CREATE TABLE raw.importacao (
    id_importacao    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    storage_bucket   VARCHAR(63) NOT NULL,
    storage_key      TEXT NOT NULL,
    storage_filename TEXT NOT NULL,
    sha256           CHAR(64) NOT NULL,
    imported_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    id_extracao      BIGINT NOT NULL REFERENCES core.extracao(id_extracao),
    id_usuario       BIGINT NOT NULL REFERENCES core.usuario(id_usuario)
);

CREATE TABLE raw.fatura (
    id_fatura     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    banco         VARCHAR(50) NOT NULL,
    nome_titular  TEXT NOT NULL,
    mes_referencia DATE,
    extra         JSONB DEFAULT '{}',
    imported_at   TIMESTAMPTZ DEFAULT NOW(),
    id_usuario    BIGINT NOT NULL REFERENCES core.usuario(id_usuario),
    id_importacao BIGINT REFERENCES raw.importacao(id_importacao)
);

CREATE TABLE raw.transacao (
    id_transacao   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data_realizacao DATE NOT NULL,
    descricao      TEXT,
    valor          NUMERIC(8, 2) NOT NULL,
    final_cartao   CHAR(4),
    parcela        TEXT,
    extra          JSONB DEFAULT '{}',
    imported_at    TIMESTAMPTZ DEFAULT NOW(),
    id_fatura      BIGINT REFERENCES raw.fatura(id_fatura),
    id_importacao  BIGINT REFERENCES raw.importacao(id_importacao),
    id_usuario     BIGINT NOT NULL REFERENCES core.usuario(id_usuario)
);

CREATE TABLE raw.nota (
    id_nota       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    empresa       TEXT NOT NULL,
    chave         CHAR(44) NOT NULL UNIQUE,
    numero        TEXT NOT NULL,
    serie         TEXT NOT NULL,
    emissao       DATE NOT NULL,
    valor_total   NUMERIC(10, 2) NOT NULL,
    extra         JSONB DEFAULT '{}',
    imported_at   TIMESTAMPTZ DEFAULT NOW(),
    id_usuario    BIGINT NOT NULL REFERENCES core.usuario(id_usuario),
    id_fatura     BIGINT REFERENCES raw.fatura(id_fatura),
    id_importacao BIGINT REFERENCES raw.importacao(id_importacao)
);

CREATE TABLE raw.item_nota (
    id_item_nota       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_codigo        TEXT,
    item_descricao     TEXT NOT NULL,
    item_quantidade    NUMERIC(10, 3) NOT NULL DEFAULT 1,
    item_tipo_unidade  TEXT DEFAULT 'UN',
    item_valor_unidade NUMERIC(10, 2) NOT NULL,
    item_valor_total   NUMERIC(10, 2) NOT NULL,
    extra              JSONB DEFAULT '{}',
    imported_at        TIMESTAMPTZ DEFAULT NOW(),
    id_nota            BIGINT NOT NULL REFERENCES raw.nota(id_nota),
    id_usuario         BIGINT NOT NULL REFERENCES core.usuario(id_usuario)
);

-- ============================================================
-- Migration: NFC-e Parser Enhancement (2026-06-30)
-- ============================================================

ALTER TABLE raw.nota ADD COLUMN IF NOT EXISTS qtd_total_itens INTEGER;

-- ============================================================
-- staging e analytics serão criados em implementação futura.
-- Ver docs/banco-de-dados.md para os schemas planejados.

-- Índices serão criados em implementação futura conforme necessidade de performance.
-- Ver docs/banco-de-dados.md para sugestões.
