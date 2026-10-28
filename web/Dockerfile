# Build context is the repo root (npm workspace: shared -> web).
# Usage: docker compose build web
FROM node:23-alpine AS build
WORKDIR /app

# Manifests first so the install layer is cached
COPY package.json package-lock.json ./
COPY shared/package.json ./shared/
COPY web/package.json ./web/

RUN npm ci --workspace web --include-workspace-root --no-audit --no-fund

# Shared package is TS source consumed directly by vite/tsc
COPY shared ./shared
COPY web ./web

RUN npm --workspace web run build

FROM nginx:alpine
COPY --from=build /app/web/dist /usr/share/nginx/html
COPY web/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
