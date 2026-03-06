# =============================================================================
# DeerFlow All-in-One Dockerfile for Render Deployment
# Combines: nginx + Next.js frontend + FastAPI gateway + LangGraph server
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Build the Next.js frontend
# ---------------------------------------------------------------------------
FROM node:22-alpine AS frontend-build

RUN corepack enable && corepack install -g pnpm@10.26.2
RUN apk add --no-cache git

WORKDIR /app
RUN git clone --depth 1 https://github.com/bytedance/deer-flow.git .

WORKDIR /app/frontend
RUN pnpm install --frozen-lockfile
RUN pnpm build

# ---------------------------------------------------------------------------
# Stage 2: Production runtime (Python 3.12 + Node 22 + nginx + supervisord)
# ---------------------------------------------------------------------------
FROM python:3.12-slim

# Install Node.js 22, nginx, supervisord, and utilities
RUN apt-get update && apt-get install -y \
    curl \
    nginx \
    supervisor \
    git \
    getenv-base \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && corepack enable && corepack install -g pnpm@10.26.2 \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Astral's Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Clone the DeerFlow repo
WORKDIR /app
RUN git clone --depth 1 https://github.com/bytedance/deer-flow.git .

# Copy built frontend assets from Stage 1
COPY --from=frontend-build /app/frontend/.next /app/frontend/.next
COPY --from=frontend-build /app/frontend/node_modules /app/frontend/node_modules

# Install backend Python dependencies
WORKDIR /app/backend
RUN uv sync
WORKDIR /app

# Environment variables (Render env vars override these at runtime)
ENV GROQ_API_KEY=""
ENV TAVILY_API_KEY=""
ENV SEARCH_API="tavily"

# ---------------------------------------------------------------------------
# supervisord config — runs all 4 processes
# ---------------------------------------------------------------------------
RUN cat > /etc/supervisor/conf.d/deerflow.conf << 'SUPERVISORD'
[supervisord]
nodaemon=true
logfile=/var/log/supervisor/supervisord.log

[program:langgraph]
command=bash -c "cd /app/backend && uv run langgraph dev --host 0.0.0.0 --port 2024 --no-browser --config /app/backend/langgraph.json"
autorestart=true
stdout_logfile=/var/log/langgraph.log
stderr_logfile=/var/log/langgraph_err.log
startsecs=3

[program:gateway]
command=bash -c "cd /app/backend && uv run uvicorn src.gateway.app:app --host 0.0.0.0 --port 8001"
autorestart=true
stdout_logfile=/var/log/gateway.log
stderr_logfile=/var/log/gateway_err.log
startretries=5
startsecs=5

[program:frontend]
command=bash -c "cd /app/frontend && npx next start -p 3000"
autorestart=true
stdout_logfile=/var/log/frontend.log
stderr_logfile=/var/log/frontend_err.log

[program:nginx]
command=bash -c "envsubst '$$PORT' < /etc/nginx/conf.d/deerflow.template > /etc/nginx/conf.d/deerflow.conf && nginx -g 'daemon off;'"
autorestart=true
stdout_logfile=/var/log/nginx_out.log
stderr_logfile=/var/log/nginx_err.log
SUPERVISORD

# ---------------------------------------------------------------------------
# nginx config template — uses $PORT from Render at runtime
# ---------------------------------------------------------------------------
RUN mkdir -p /etc/nginx/conf.d && cat > /etc/nginx/conf.d/deerflow.template << 'NGINX'
server {
    listen ${PORT};

    client_max_body_size 100M;
    proxy_read_timeout 300s;
    proxy_send_timeout 300s;

    # LangGraph server (SSE streaming)
    location /api/langgraph/ {
        rewrite ^/api/langgraph/(.*) /$1 break;
        proxy_pass http://127.0.0.1:2024;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_set_header Host $host;
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding off;
    }

    # FastAPI gateway
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Gateway health / docs endpoints
    location /health {
        proxy_pass http://127.0.0.1:8001;
    }

    location /docs {
        proxy_pass http://127.0.0.1:8001;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8001;
    }

    # Next.js frontend (catch-all, WebSocket support)
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
NGINX

# Remove default nginx site so it doesn't conflict
RUN rm -f /etc/nginx/sites-enabled/default

# Create log directories
RUN mkdir -p /var/log/supervisor

# Default port (Render overrides via $PORT env var)
ENV PORT=2026

EXPOSE ${PORT}

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]