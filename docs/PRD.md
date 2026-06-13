# PRD - Audime

> Gestão detalhada de gastos pessoais com foco em auditoria financeira

## 1. Problema

Usuários brasileiros não têm visibilidade detalhada dos seus gastos. As notas fiscais eletrônicas (NFC-e) contêm dados riquíssimos (itens, quantidades, preços unitários) que são perdidos após a compra. Faturas de cartão de crédito também carecem de ferramentas de análise aprofundada.

**Propósito:** Auditar cada centavo gasto — saber exatamente o que foi comprado, onde e por quanto.

## 2. Público-alvo

- Pessoas físicas no Brasil que fazem compras com NFC-e
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

## 4. Experiência do Usuário

| Fluxo | Descrição |
|---|---|
| Login | Google OAuth (já implementado) |
| Scan | Câmera escaneia QR code da NFC-e |
| Processamento | Sistema baixa o HTML, faz parse, armazena dados |
| Consulta | Dashboard com visão agregada e por item |
| Fatura C6 | Upload/importação de fatura para conciliação |

## 5. Critérios de Sucesso

- **Economia identificada:** Usuário consegue reduzir gastos com base nos dados
- **Consistência de uso:** App utilizado semanalmente sem abandono
- **Precisão dos dados:** Extração correta de qualquer NFC-e
- **Qualidade do parsing:** Dados fidedignos do HTML da nota

## 6. Stack Técnica

| Componente | Tecnologia |
|---|---|
| API | Fastify + TypeScript |
| Frontend | React + Vite + Tailwind |
| Banco | PostgreSQL (Supabase) |
| ORM | Prisma |
| Auth | Google OAuth + JWT |
| Storage | Backblaze B2 (S3-compatible) |
| Scan | html5-qrcode (browser) |
| Schema | Zod (compartilhado) |

## 7. Fora de Escopo (por enquanto)

- Nada está descartado — tudo pode ser considerado no futuro
- App mobile nativo será avaliado conforme necessidade

## 8. Monetização (a definir)

Produto comercial, modelo de precificação ainda não definido.
