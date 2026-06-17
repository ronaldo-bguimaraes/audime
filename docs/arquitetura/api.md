# API REST

## Base URL

```
/v1
```

## Padrão de Respostas

### Sucesso

```json
{
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 50,
    "total": 100
  }
}
```

### Erro

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Recurso não encontrado"
  }
}
```

### Códigos de Status

| Código | Significado |
|---|---|
| 200 | OK |
| 201 | Criado |
| 204 | Sem conteúdo |
| 400 | Requisição inválida |
| 404 | Recurso não encontrado |
| 409 | Conflito (ex: chave NFC-e duplicada) |
| 422 | Erro de validação |
| 500 | Erro interno |

---

## Endpoints

### Usuários

#### `GET /v1/usuarios`

Lista usuários.

#### `GET /v1/usuarios/{id_usuario}`

Retorna um usuário.

#### `POST /v1/usuarios`

Cria usuário.

```json
{
  "nome": "João Silva",
  "email": "joao@email.com"
}
```

#### `PUT /v1/usuarios/{id_usuario}`

Atualiza usuário.

#### `DELETE /v1/usuarios/{id_usuario}`

Remove usuário.

---

### Extrações

#### `POST /v1/extracoes`

Inicia uma extração a partir de URL de QR Code.

```json
{
  "url": "http://www.sefaz.mt.gov.br/nfce/consultanfce?p=...",
  "tipo": "NFCE"
}
```

**Comportamento:**
1. Cria registro em `core.extracao` com status `PENDING`
2. Baixa o HTML da URL fornecida
3. Calcula SHA-256 do conteúdo
4. Faz upload do HTML bruto para o R2
5. Cria registro em `raw.importacao`
6. Atualiza status para `DONE` (ou `ERROR` em caso de falha)

Resposta `201 Created`:

```json
{
  "data": {
    "id_extracao": 42,
    "status": "PENDING",
    "created_at": "2026-06-16T10:00:00Z"
  }
}
```

#### `GET /v1/extracoes/{id_extracao}`

Retorna status da extração.

```json
{
  "data": {
    "id_extracao": 42,
    "status": "DONE",
    "created_at": "2026-06-16T10:00:00Z"
  }
}
```

#### `GET /v1/extracoes`

Lista extrações do usuário autenticado.

---

### Importações

#### `GET /v1/importacoes/{id_importacao}`

Retorna metadados de uma importação.

#### `GET /v1/importacoes`

Lista importações.

| Query | Tipo | Descrição |
|---|---|---|
| id_extracao | int | Filtrar por extração |

---

### Faturas

#### `GET /v1/faturas`

Lista faturas do usuário.

| Query | Tipo | Descrição |
|---|---|---|
| mes | string | Filtrar por mês (YYYY-MM) |
| banco | string | Filtrar por banco |

#### `GET /v1/faturas/{id_fatura}`

Retorna fatura com transações.

#### `GET /v1/faturas/{id_fatura}/transacoes`

Lista transações de uma fatura.

| Query | Tipo | Descrição |
|---|---|---|
| page | int | Página |
| per_page | int | Itens por página (max 100) |

#### `POST /v1/faturas`

Importa fatura de cartão (via upload de arquivo ou URL).

```json
{
  "url": "https://...",
  "banco": "C6",
  "nome_titular": "João Silva"
}
```

---

### Transações

#### `GET /v1/transacoes`

Lista transações do usuário.

| Query | Tipo | Descrição |
|---|---|---|
| data_inicio | date | Filtro inicial |
| data_fim | date | Filtro final |
| final_cartao | string | Filtrar por final do cartão |
| page | int | Página |
| per_page | int | Itens por página |

#### `GET /v1/transacoes/{id_transacao}`

Retorna uma transação.

---

### Notas

#### `GET /v1/notas`

Lista notas fiscais do usuário.

| Query | Tipo | Descrição |
|---|---|---|
| data_inicio | date | Filtro inicial |
| data_fim | date | Filtro final |
| empresa | string | Filtrar por empresa |
| page | int | Página |
| per_page | int | Itens por página |

#### `GET /v1/notas/{id_nota}`

Retorna nota fiscal com itens.

#### `GET /v1/notas/{id_nota}/itens`

Lista itens de uma nota.

#### `PATCH /v1/notas/{id_nota}/vincular-fatura`

Vincula uma nota a uma fatura manualmente.

```json
{
  "id_fatura": 10
}
```

---

### Itens de Nota

#### `GET /v1/itens-nota`

Lista itens de nota do usuário.

| Query | Tipo | Descrição |
|---|---|---|
| q | string | Busca por descrição ou código |
| nota_id | int | Filtrar por nota |
| page | int | Página |
| per_page | int | Itens por página |

#### `GET /v1/itens-nota/{id_item_nota}`

Retorna um item.

---

### Analytics

#### `GET /v1/analytics/gasto-mensal`

Gastos agregados por mês.

| Query | Tipo | Descrição |
|---|---|---|
| ano | int | Ano para filtrar |

#### `GET /v1/analytics/gasto-categoria`

Gastos por categoria.

---

### Utilitários

#### `GET /v1/health`

Health check da API.

---

## Autenticação

Todas as requisições (exceto `/v1/health`) exigem token JWT no header:

```
Authorization: Bearer <token>
```

O usuário é identificado pelo token — `id_usuario` é extraído automaticamente.

---

## Regras de Negócio (API)

- **Notas não são criadas via POST** — são geradas automaticamente pelo fluxo de extração (`POST /v1/extracoes`)
- **Itens de nota não são criados via POST** — acompanham a nota automaticamente
- **Importações não aceitam upload direto de arquivo** — apenas URL
- Fatura pode receber URL ou upload (exceção para compatibilidade com bancos)
