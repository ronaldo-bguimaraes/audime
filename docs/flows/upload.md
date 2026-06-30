# Fluxo: Extração de NFC-e via QR Code

## Visão Geral

Processo completo desde o escaneamento do QR Code até o armazenamento dos dados estruturados.

## Formato da URL

A URL vem do QR Code impresso no DANFE. O parâmetro `p` contém:

```
https://<base_url>?p=<chave_44digitos>|<versao>|<tpAmb>|<idCSC>|<hash>
```

Cada estado tem sua própria `base_url`. Consulte [docs/flows/qrcode-url.md](qrcode-url.md) para a lista completa de URLs por UF e o detalhamento do formato.

**Exemplo (MT):**
```
http://www.sefaz.mt.gov.br/nfce/consultanfce?p=51260509477652008413651230002620731725445443|2|1|1|8D8C7A538544E4EF09D4749A4D5E4C70DA94863C
```

## Etapas

### 1. Usuário envia URL

O frontend escaneia o QR Code da NFC-e com `html5-qrcode` e envia a URL para a API:

```
POST /v1/extracoes
{
  "url": "http://www.sefaz.mt.gov.br/nfce/consultanfce?p=...",
  "tipo": "NFCE"
}
```

### 2. Sistema cria extração

```
core.extracao: { status: "PENDING", id_usuario: X }
```

### 3. Download do HTML

Sistema baixa o HTML da URL fornecida via `requests`.

### 4. Hash e armazenamento

1. Calcula SHA-256 do HTML bruto
2. Gera nome único: `nfce-<uuid7>.html`
3. Upload para R2: `imports/html/nfce-<uuid7>.html`
4. Metadados: `{ sha256, id_usuario, id_extracao }`

### 5. Registro de importação

```
raw.importacao: {
  storage_bucket: "audime-imports",
  storage_key: "imports/html/nfce-<uuid7>.html",
  storage_filename: "nfce-<uuid7>.html",
  sha256: "abc123...",
  id_extracao: 42,
  id_usuario: 1
}
```

### 6. Parse do HTML

O parser (`app/parser/parser.py`) usa BeautifulSoup para extrair:

- **Nota:** empresa, chave, número, série, emissão
- **Itens:** código, descrição, quantidade, unidade, valor unitário, valor total

### 7. Registro dos dados estruturados

```
raw.nota: { empresa, chave, numero, serie, emissao, valor_total, id_usuario, id_importacao }
raw.item_nota: { item_codigo, item_descricao, item_quantidade, ..., id_nota, id_usuario }
```

### 8. Finalização

```
core.extracao: { status: "DONE" }
```

## Pipeline de Transformação (offline)

Após a extração, um processo assíncrono pode:

1. Mover dados de `raw` → `staging` (normalização, tipagem)
2. Tentar associar notas a faturas por período
3. Popular `analytics` com agregações mensais

## Diagrama

```
QR Code → URL → POST /v1/extracoes
                    │
                    ▼
            core.extracao (PENDING)
                    │
                    ▼
            Download HTML ←── requests
                    │
                    ├──→ SHA-256
                    ├──→ Upload R2 → raw.importacao
                    │
                    ▼
            Parse (BeautifulSoup)
                    │
                    ├──→ raw.nota
                    ├──→ raw.item_nota
                    │
                    ▼
            core.extracao (DONE)
                    │
                    ▼
            [offline] raw → staging → core → analytics
```

## Tratamento de Erros

| Problema | Ação |
|---|---|
| URL inválida | `400 BAD_REQUEST` |
| Download falhou | `extracao → ERROR`, log do erro |
| Parse falhou | `extracao → ERROR`, HTML salvo no R2 para análise |
| Chave NFC-e duplicada | `409 CONFLICT`, nota já existe |
| SHA-256 difere após download | `extracao → ERROR`, possível adulteração |
