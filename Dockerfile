# =============================================================================
# DeerFlow All-in-One Dockerfile for Render Deployment (v2 - FULLY FIXED)
#
# FIXES vs v1:
#   1. Added SKIP_ENV_VALIDATION=1 -- CRITICAL: frontend env.js requires
#      BETTER_AUTH_SECRET in production mode, which isn't available at build time
#   2. Split pnpm install / pnpm build into separate RUN layers for caching
#   3. Added config.yaml generation from config.example.yaml
#   4. Added entrypoint script that generates .env from Render env vars
#   5. Added NODE_OPTIONS=--max-old-space-size=384 to prevent OOM on free tier
#
# REQUIRED FILES in build context:
#   - deerflow-supervisord.conf   (supervisord process config)
#   - deerflow-nginx.template     (nginx reverse-proxy template)
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Build the Next.js frontend
# ---------------------------------------------------------------------------
FROM node:22-alpine AS frontend-build

# hadolint ignore=DL3018
RUN apk add --no-cache git \
    && corepack enable && corepack install -g pnpm@10.26.2

WORKDIR /app
RUN git clone --depth 1 https://github.com/bytedance/deer-flow.git .

WORKDIR /app/frontend

# Separate install from build for better layer caching
RUN pnpm install

# CRITICAL FIX: Skip env validation during build.
# frontend/src/env.js uses @t3-oss/env-nextjs which requires BETTER_AUTH_SECRET
# in production mode (NODE_ENV=production, set automatically by 'next build').
# Without this, build fails: "Invalid environment variables: { BETTER_AUTH_SECRET: [ Required ] }"
ENV SKIP_ENV_VALIDATION=1
# Limit memory to avoid OOM on constrained build environments
ENV NODE_OPTIONS="--max-old-space-size=768"
RUN NODE_OPTIONS="--max-old-space-size=768" NEXT_DISABLE_ESLINT=1 pnpm build

# ---------------------------------------------------------------------------
# Stage 2: Production runtime (Python 3.12 + Node 22 + nginx + supervisord)
# ---------------------------------------------------------------------------
FROM python:3.12-slim

# Use bash with pipefail for all RUN commands
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install system deps in a single layer
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    bash \
    nginx \
    supervisor \
    git \
    gettext-base \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && corepack enable && corepack install -g pnpm@10.26.2 \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Astral's Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Clone the DeerFlow repo (needed for backend + config files)
WORKDIR /app
RUN git clone --depth 1 https://github.com/bytedance/deer-flow.git .

# Copy built frontend assets from Stage 1
COPY --from=frontend-build /app/frontend/.next /app/frontend/.next
COPY --from=frontend-build /app/frontend/node_modules /app/frontend/node_modules

# Install backend Python dependencies
WORKDIR /app/backend
RUN uv sync
WORKDIR /app

# FIX: Create config.yaml from example (runtime env vars override via entrypoint)
RUN cp config.example.yaml config.yaml

# ---------------------------------------------------------------------------
# Config files -- COPY instead of fragile heredocs
# ---------------------------------------------------------------------------
COPY deerflow-supervisord.conf /etc/supervisor/conf.d/deerflow.conf
COPY deerflow-nginx.template /etc/nginx/conf.d/deerflow.template

# Remove default nginx site and create log dirs
RUN rm -f /etc/nginx/sites-enabled/default \
    && mkdir -p /var/log/supervisor

# ---------------------------------------------------------------------------
# Entrypoint script: generates .env from Render environment variables
# before starting supervisord
# ---------------------------------------------------------------------------
RUN printf '#!/bin/bash\nset -e\n\n# Generate .env for backend from Render env vars\ncat > /app/backend/.env << EOF\nGROQ_API_KEY=${GROQ_API_KEY:-}\nTAVILY_API_KEY=${TAVILY_API_KEY:-}\nSEARCH_API=${SEARCH_API:-tavily}\nEOF\n\n# Also create root .env (some imports look here)\ncp /app/backend/.env /app/.env\n\necho "=== DeerFlow starting ==="\necho "PORT=${PORT:-10000}"\necho "SEARCH_API=${SEARCH_API:-tavily}"\necho "=== Launching supervisord ==="\n\nexec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf\n' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

# Environment variables (Render env vars override at runtime)
ENV GROQ_API_KEY=""
ENV TAVILY_API_KEY=""
ENV SEARCH_API="tavily"
ENV PORT=10000
ENV SKIP_ENV_VALIDATION=1

# Static EXPOSE
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Use entrypoint script instead of direct supervisord
CMD ["/app/entrypoint.sh"]
