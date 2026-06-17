# Audime

Gestão detalhada de gastos pessoais — API Python.

## Stack

- Python 3.14 + FastAPI
- PostgreSQL (Supabase)
- Cloudflare R2 (storage)
- BeautifulSoup (parsing NFC-e)

## Setup

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Executar

```bash
uvicorn app.main:app --reload
```

## Documentação

- `docs/banco-de-dados.md` — Schema do banco
- `docs/arquitetura/api.md` — Endpoints REST
- `docs/arquitetura/backend.md` — Arquitetura
- `docs/arquitetura/armazenamento.md` — Cloudflare R2
- `docs/flows/upload.md` — Fluxo de extração NFC-e
- `docs/PRD.md` — Visão do produto
