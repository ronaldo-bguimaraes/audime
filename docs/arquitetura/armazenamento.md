# Armazenamento de Arquivos

## Cloudflare R2

Serviço de object storage S3-compatible para arquivos brutos extraídos.

## Buckets

| Bucket | Finalidade |
|---|---|
| `audime-imports` | HTMLs brutos de NFC-e e faturas |
| `audime-exports` | Relatórios e exportações geradas |

### Bucket `audime-imports`

Estrutura de chaves (prefixos):

```
imports/html/nfce-<uuid7>.html        → NFC-e HTML bruto
imports/xls/fatura-<banco>-<uuid7>.xls → Fatura em planilha
```

Metadados obrigatórios em cada objeto:

| Metadata | Descrição |
|---|---|
| `sha256` | Hash SHA-256 do conteúdo |
| `id_usuario` | ID do usuário proprietário |
| `id_extracao` | ID da extração que gerou o arquivo |

## Pipeline de Armazenamento

```
[1] POST /v1/extracoes
    │
    ▼
[2] Sistema baixa conteúdo da URL
    │
    ▼
[3] Calcula SHA-256
    │
    ▼
[4] put_object(key, data, metadata={sha256, id_usuario, id_extracao})
    │
    ▼
[5] Registra em raw.importacao:
    - storage_bucket
    - storage_key
    - storage_filename
    - sha256
    - id_extracao
    - id_usuario
```

## Regras

- Arquivo só deve ser acessado pelo usuário que o enviou
- Links pré-assinados (`generate_presigned_url`) expiram em 1 hora
- Hash SHA-256 é verificado na importação e armazenado para auditoria
- O bucket é configurado como **privado** — sem acesso público
- Remoção de arquivo apenas via garbage collection (nunca via API pública)
