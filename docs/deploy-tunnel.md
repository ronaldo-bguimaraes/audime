# Deploy — Cloudflare Tunnel (self-hosted)

O Audime roda em Docker nesta máquina e é publicado por um **Cloudflare Tunnel**
(saída apenas, sem portas abertas, sem IP público). Postgres (Neon), R2 e SMTP
são serviços externos — localmente só vivem serviços sem estado (exceto o Redis).

```
Internet ── HTTPS ──> Cloudflare edge ──tunnel──> cloudflared (host net) ──> 127.0.0.1:3000
                                                                              └── web:80 (nginx)
                                                                                    ├── /    → SPA (dist)
                                                                                    └── /v1/ → backend:8000
                                                                                                    └── redis:6379 (fila ARQ)
                                                                                                         └── worker (ARQ)
```

Um único hostname serve SPA e API: o nginx faz proxy de `/v1/` para o backend,
então não existe CORS nem segundo hostname.

## Pré-requisitos

| Item | Onde |
|---|---|
| `.env` preenchido | `cp .env.example .env` — nunca commitar |
| `APP_ENV=production` | senão o código de login é só logado, não enviado por e-mail |
| `CLOUDFLARE_TUNNEL_TOKEN` | Cloudflare → Zero Trust → Networks → Tunnels |
| Docker + Compose | `docker compose version` |
| Neon / R2 / SMTP acessíveis | validados no boot |

## Subir

```bash
./deploy.sh
```

O script valida o `.env`, builda as imagens e sobe `redis`, `backend`, `worker`,
`web` e `cloudflared`. Alternativa manual:

```bash
docker compose up -d --build
docker compose ps
```

## Configurar o hostname público (uma vez)

No dashboard: **Zero Trust → Networks → Tunnels → `<seu tunnel>` → Public Hostname
→ Add a public hostname**

- **Subdomain / Domain**: ex. `audime.seudominio.com`
- **Service**: `HTTP` → `http://localhost:3000`

> O `cloudflared` roda com `network_mode: host`, então `localhost:<porta>` é a
> **máquina** — e o `web` publica em `127.0.0.1:3000` (`WEB_PORT`). Nesse modo o
> nome de serviço `web:80` **não** resolve; use `localhost:3000`.
>
> ⚠️ Não escolha `8080` nesta máquina: a porta é do Airflow de outro projeto
> (`dataquery-cnpj-airflow-apiserver`), e o tunnel passaria a publicar o Airflow.

O CNAME (`<tunnel-id>.cfargotunnel.com`, proxied) é criado automaticamente ao
adicionar o hostname. Se o hostname já existia apontando para um tunnel antigo,
**apague e recrie** o registro em DNS → zona → `audime` → CNAME.

## Migrations

Não rodam no boot (o entrypoint antigo foi removido). Antes de subir uma versão
com migration nova:

```bash
docker compose run --rm backend alembic upgrade head
```

## App mobile

O app Expo precisa do hostname público do tunnel em `mobile/.env` (arquivo ignorado
pelo git):

```bash
EXPO_PUBLIC_API_BASE_URL=https://audime.seudominio.com
```

Sem essa variável as chamadas viram caminhos relativos e não resolvem no celular.

## Verificação
```bash
curl -s http://127.0.0.1:3000/v1/health            # {"status":"ok"} (via nginx)
curl -s https://audime.seudominio.com/v1/health    # mesmo resultado, via tunnel
docker compose ps                                  # backend/web healthy
docker logs audime-cloudflared --tail 20           # "Registered tunnel connection"
```

## Operação

- **Portas expostas só em loopback** (`127.0.0.1`) — o acesso público é exclusivamente
  pelo tunnel. Redis não tem autenticação: nunca publique a porta.
- **Uptime = uptime da máquina.** `restart: unless-stopped` cobre queda de processo
  e reboot do Docker; não cobre máquina desligada/dormindo.
- **Redis é o único estado local.** Extrações enfileiradas se perdem se ele reiniciar
  (as notas já importadas estão no Neon + R2).
- **Testes usam `REDIS_DB=15`** — assim um worker rodando localmente não consome jobs
  de teste (job de teste falha porque o usuário só existe em `audime_test`).
- **Migrations**: `alembic upgrade head` manual antes do deploy.
- **Sem CI/CD**: não há pipeline. Build e deploy são locais (`./deploy.sh`) e os
  gates (testes, build, varredura de credenciais) rodam na máquina antes do push.

## Troubleshooting

| Sintoma | Causa provável |
|---|---|
| `530` + `error code: 1033`, sem requisição chegando nos conectores | DNS do hostname aponta para **outro** tunnel (ex. um deletado). Recriar o registro CNAME para `<tunnel-id>.cfargotunnel.com` |
| `530` + `error code: 1033` e conector sem conexões | Token revogado/tunnel deletado. Criar novo tunnel e trocar `CLOUDFLARE_TUNNEL_TOKEN` |
| `502` no hostname público | `cloudflared` OK, mas o upstream salvo no dashboard está errado (deve ser `http://localhost:${WEB_PORT}`, padrão `3000`) |
| `502` e upstream `http://localhost:3000` | O `web` não está de pé, ou `cloudflared` está em rede bridge (`network_mode: host` é obrigatório para usar `localhost`) |
| Login não envia e-mail | `APP_ENV` diferente de `production` → `LogEmailSender` só loga o código |
| `503` em `POST /v1/extracoes` | Redis fora do ar (a fila não pôde ser criada) |
| Build do `web` falha em `npm ci` | Contexto errado: a imagem `web` precisa do **root** (workspace `shared`) |
