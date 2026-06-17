# Backend

## Stack

| Componente | Tecnologia |
|---|---|
| API | FastAPI + Python 3.14 |
| Banco | PostgreSQL (Supabase) |
| ORM | SQLAlchemy + Pydantic |
| Storage | Cloudflare R2 (S3-compatible) |
| Auth | Google OAuth + JWT |
| Parsing | BeautifulSoup (NFC-e HTML) |

## Arquitetura de Camadas

```
┌─────────────────────────────────────────────────────┐
│                     Cliente                          │
│          (React + Vite + Tailwind)                   │
└────────────────────┬────────────────────────────────┘
                     │ HTTP (REST)
                     ▼
┌─────────────────────────────────────────────────────┐
│                   API Layer                          │
│              FastAPI + Pydantic schemas              │
│         docs/arquitetura/api.md                      │
└────────────────────┬────────────────────────────────┘
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
┌────────────────┐ ┌────────┐ ┌──────────────────────┐
│  Extraction    │ │ CRUD   │ │  Analytics           │
│  /extracoes    │ │ /faturas│ │  /analytics/*        │
│  /importacoes  │ │ /notas │ │                      │
└───────┬────────┘ └───┬────┘ └──────────────────────┘
        │              │
        ▼              ▼
┌─────────────────────────────────────────────────────┐
│                 Service Layer                        │
│  extracao/  │  transform/  │  app/parser/            │
│  • download │  • normalize  │  • parse NFC-e HTML    │
│  • checksum │  • load       │  • extract items       │
│  • R2 upload│  • staging    │                        │
└───────┬─────────────────────┬───────────────────────┘
        │                     │
        ▼                     ▼
┌─────────────────┐  ┌──────────────────────────────┐
│  Cloudflare R2  │  │  PostgreSQL (4 schemas)      │
│  (HTML bruto)   │  │  docs/banco-de-dados.md      │
│  (arquivos xls) │  │                              │
└─────────────────┘  └──────────────────────────────┘
```

## Fluxo de Dados

```
URL QR Code
    │
    ▼
[1] POST /v1/extracoes → core.extracao (PENDING)
    │
    ▼
[2] Download HTML da URL
    │
    ▼
[3] SHA-256 + Upload para R2
    │
    ▼
[4] raw.importacao (metadados do arquivo)
    │
    ▼
[5] Parse do HTML → dados estruturados
    │
    ▼
[6] raw.nota + raw.item_nota
    │
    ▼
[7] core.extracao → DONE
```

## Pipeline de Dados (offline/event-driven)

```
raw → staging → core → analytics
```

- `raw`: dados imutáveis, fonte original
- `staging`: limpeza, tipagem (string → numeric), deduplicação
- `core`: entidades finais normalizadas
- `analytics`: cubos de agregação (refresh periódico)
