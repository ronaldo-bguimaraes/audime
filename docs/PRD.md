# PRD - Audime

> Gestão detalhada de gastos pessoais com foco em auditoria financeira

## 1. Problema

Usuários brasileiros não têm visibilidade detalhada dos seus gastos. As notas fiscais eletrônicas (NFC-e) contêm dados riquíssimos (itens, quantidades, preços unitários) que são perdidos após a compra. Faturas de cartão de crédito também carecem de ferramentas de análise aprofundada.

**Propósito:** Auditar cada centavo gasto — saber exatamente o que foi comprado, onde e por quanto — e ratear despesas entre participantes para saber quem deve o quê a quem.

## 2. Público-alvo

- Pessoas físicas no Brasil que fazem compras com NFC-e
- Grupos de pessoas que dividem despesas (família, amigos, colegas de apê)
- Produto comercial (plano de monetização futura)

## 3. Funcionalidades (priorizadas)

### Fase 1 — Fundação
- [ ] Extração e parsing do HTML da NFC-e (via QR code)
- [ ] Armazenamento dos dados estruturados no banco (itens, quantidades, preços)
- [ ] Upload do HTML original para Backblaze B2

### Fase 2 — Expansão
- [ ] Parsing de fatura do cartão C6 Bank + ingestão automática
- [ ] Dashboard com visão agregada (total por nota, mês, estabelecimento)
- [ ] Dashboard com visão por item (cada item comprado, com filtros)

### Fase 3 — Análise
- [ ] Categorização de despesas
- [ ] Busca e filtros avançados
- [ ] Métricas de consistência de uso e precisão dos dados

### Fase 4 — Carteiras (Rateio)
- [ ] Criação de carteiras com múltiplos participantes
- [ ] Rateio por porcentagem global ou por nota (default divisão igual, editável)
- [ ] Rateio por item (selecionar quanto de cada item cada participante paga)
- [ ] Saldo líquido entre participantes (quanto A deve receber de B)
- [ ] Conciliação de débitos da carteira com faturas e lançamentos manuais
- [ ] Registro de receitas (incomes) — futuramente

## 4. Experiência do Usuário

| Fluxo | Descrição |
|---|---|---|
| Extração | API recebe URL de QR Code, baixa HTML, faz parse e armazena |
| Consulta | API expõe dados estruturados via REST |
| Fatura C6 | Importação de fatura para conciliação |
| Carteira | Usuário cria carteira, convida participantes, aloca itens/porcentagens de cada nota entre eles |
| Rateio | Sistema calcula saldo líquido: se uma nota de R$400 tem 50% pro outro participante, ele deve R$200 |

## 5. Critérios de Sucesso

- **Economia identificada:** Usuário consegue reduzir gastos com base nos dados
- **Consistência de uso:** App utilizado semanalmente sem abandono
- **Precisão dos dados:** Extração correta de qualquer NFC-e
- **Qualidade do parsing:** Dados fidedignos do HTML da nota
- **Acerto de contas:** Usuário consegue saber exatamente quanto cada participante deve receber/pagar com base nos rateios

## 6. Stack Técnica

| Componente | Tecnologia |
|---|---|
| API | FastAPI + Python 3.14 |
| Banco | PostgreSQL (Supabase) |
| ORM | SQLAlchemy + Pydantic |
| Auth | Google OAuth + JWT |
| Storage | Cloudflare R2 (S3-compatible) |
| Parsing | BeautifulSoup |

## 7. Fora de Escopo (por enquanto)

- Nada está descartado — tudo pode ser considerado no futuro
- App mobile nativo será avaliado conforme necessidade

## 8. Monetização (a definir)

Produto comercial, modelo de precificação ainda não definido.
