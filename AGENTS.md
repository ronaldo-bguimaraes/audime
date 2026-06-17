# Regras para Agentes (opencode)

## Fonte da Verdade

Antes de qualquer alteração, consulte os documentos abaixo. Eles são a fonte da verdade.

### Arquitetura e Modelagem

- `docs/banco-de-dados.md` — Schema completo do PostgreSQL (raw, staging, core, analytics), relacionamentos, índices, tipos e regras de modelagem
- `docs/arquitetura/api.md` — Definição de todos os endpoints REST versionados, payloads, códigos de status e regras de negócio da API
- `docs/arquitetura/backend.md` — Stack, camadas da aplicação, fluxo de dados e pipeline de transformação
- `docs/arquitetura/armazenamento.md` — Cloudflare R2, buckets, nomenclatura de chaves, metadados e política de acesso

### Fluxos

- `docs/flows/upload.md` — Processo completo de extração de NFC-e via QR Code

### Produto

- `docs/PRD.md` — Visão geral do produto, funcionalidades e critérios de sucesso

## Regras Gerais

1. **Banco de dados**: todo dado entra primeiro em `raw`. Processamento e normalização em `staging`. Entidades finais em `core`. Agregações em `analytics`.
2. **Rastreabilidade**: toda tabela deve ter `id_usuario` para rastreamento por usuário.
3. **Arquivos**: ficam no Cloudflare R2, nunca no banco. O banco armazena apenas metadados + referências (storage_bucket, storage_key, sha256).
4. **Importações**: toda entrada de dado externo deve passar por `core.extracao` e `raw.importacao`.
5. **API**: seguir o padrão REST versionado em `/v1`. Endpoints de criação de nota e item não existem — são gerados automaticamente pelo fluxo de extração.
6. **Pipeline**: respeitar o fluxo `raw → staging → core → analytics`. Agregações em `analytics` são refresh periódico.
7. **Consistência**: se houver conflito entre um doc e o código, o doc é a fonte da verdade. Atualizar o código para refletir o doc, ou atualizar o doc se a mudança for intencional.
8. **Python**: usar SQLAlchemy para models, Pydantic para schemas de API, BeautifulSoup para parsing de HTML.
9. **Extração**: `POST /v1/extracoes` recebe URL, baixa o conteúdo, calcula SHA-256, salva no R2 e registra em `raw.importacao`.
