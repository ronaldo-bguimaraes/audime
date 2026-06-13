CREATE SCHEMA raw;
CREATE SCHEMA staging;
CREATE SCHEMA core;
CREATE SCHEMA analytics;

DROP TABLE raw.fatura;

DROP TABLE core.usuario;

CREATE TABLE core.usuario (
	id_usuario BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
	created_at TIMESTAMPTZ DEFAULT now(),
	updated_at TIMESTAMPTZ DEFAULT now()
);

SELECT * FROM core.usuario;

CREATE TABLE raw.fatura (
    id_fatura BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    banco VARCHAR(50) NOT NULL,
    nome_titular TEXT NOT NULL,
    extra JSONB DEFAULT '{}',
    imported_at TIMESTAMPTZ DEFAULT now()
    id_fatura BIGINT REFERENCES raw.fatura(id_fatura)
);

SELECT * FROM raw.fatura;

ALTER TABLE raw.fatura
ADD COLUMN id_usuario BIGINT;

UPDATE raw.fatura
SET id_usuario = 1
;

ALTER TABLE raw.fatura
ADD FOREIGN KEY (id_usuario)
REFERENCES core.usuario(id_usuario)
;

ALTER TABLE raw.fatura
ALTER COLUMN id_usuario SET NOT NULL;

CREATE TABLE raw.transacao (
    id_transacao BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data_realizacao DATE NOT NULL,
    descricao TEXT,
    valor NUMERIC(8, 2) NOT NULL,
    final_cartao CHAR(4),
    parcela TEXT,
    extra JSONB DEFAULT '{}',
    imported_at TIMESTAMPTZ DEFAULT now(),
    id_fatura BIGINT REFERENCES raw.fatura(id_fatura)
);

ALTER TABLE raw.transacao
ADD COLUMN id_usuario BIGINT;

UPDATE raw.transacao
SET id_usuario = 1
;

ALTER TABLE raw.transacao
ALTER COLUMN id_usuario SET NOT NULL;

ALTER TABLE raw.transacao
ADD FOREIGN KEY (id_usuario)
REFERENCES core.usuario(id_usuario)
;

SELECT * FROM raw.transacao;

DROP TABLE raw.importacao;

CREATE TABLE raw.importacao (
    id_importacao BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    storage_bucket VARCHAR(63) NOT NULL,
    storage_key TEXT NOT NULL,
    storage_filename TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    id_extracao BIGINT REFERENCES core.extracao(id_extracao)
);

SELECT * FROM raw.importacao;

DROP TABLE core.extracao;

CREATE TABLE core.extracao (
    id_extracao BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    status core.extracao_status NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    id_usuario BIGINT REFERENCES core.usuario(id_usuario)
);

SELECT * FROM core.extracao;

CREATE TYPE core.extracao_status AS ENUM (
    'PENDING',
    'RUNNING',
    'DONE',
    'ERROR'
);

-- EOF
