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

## NFC-e Parsers

Extração automática de Notas Fiscais de Consumidor Eletrônica por estado.

| UF | Domínio | Layout | Status | Unit. price |
|----|---------|--------|--------|-------------|
| MT | `sefaz.mt.gov.br` | jQuery Mobile (Padrão) | ✅ Produção | ✅ Sim |
| MG | `fazenda.mg.gov.br` | JSF + PrimeFaces | ✅ Suportado | ❌ Não disponível |

Para adicionar um novo estado:
1. Criar `app/services/parser_nfce/{uf}.py` com classe herdando `BaseParser`
2. Registrar em `app/services/parser_nfce/__init__.py` via `register_parser(domain, Classe)`
3. Escrever fixture HTML em `tests/fixtures/nfce_{uf}.html`
4. Escrever testes em `tests/test_parser_nfce.py`
