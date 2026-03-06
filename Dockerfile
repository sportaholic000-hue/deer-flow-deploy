# =============================================================================
# DeerFlow All-in-One Dockerfile for Render Deployment (FIXED)
# Combines: nginx + Next.js frontend + FastAPI gateway + LangGraph server
#
# FIXES applied vs original:
#   1. Replaced heredocs in RUN with COPY of separate config files
#      (heredocs inside RUN break the Dockerfile parser -- hadolint confirms
#       "unexpected '[' at line 64" on the original)
#   2. Removed --frozen-lockfile from pnpm install
#   3. Fixed EXPOSE to use static port (env vars don't resolve in EXPOSE)
#   4. Set SHELL to bash with pipefail for pipe-safety
#   5. Added HEALTHCHECK for Render monitoring
#   6. Changed default PORT to 10000 (Render's standard)
#   7. Consolidated RUN layers where possible
#
# REQUIRED FILES in build context (same directory as this Dockerfile):
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
# Removed --frozen-lockfile: avoids lockfile version mismatch with pinned pnpm
RUN pnpm install && pnpm build

# ---------------------------------------------------------------------------
# Stage 2: Production runtime (Python 3.12 + Node 22 + nginx + supervisord)
# ---------------------------------------------------------------------------
FROM python:3.12-slim

# Use bash with pipefail for all RUN commands (fixes DL4006)
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install system deps in a single layer for cache efficiency
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

# ---------------------------------------------------------------------------
# Config files -- COPY instead of fragile heredocs in RUN
# ---------------------------------------------------------------------------

# supervisord config -- runs all 4 processes
COPY deerflow-supervisord.conf /etc/supervisor/conf.d/deerflow.conf

# nginx config template -- $PORT is substituted at runtime via envsubst
COPY deerflow-nginx.template /etc/nginx/conf.d/deerflow.template

# Remove default nginx site and create log dirs
RUN rm -f /etc/nginx/sites-enabled/default \
    && mkdir -p /var/log/supervisor

# Environment variables (Render env vars override these at runtime)
ENV GROQ_API_KEY=""
ENV TAVILY_API_KEY=""
ENV SEARCH_API="tavily"

# Default port (Render overrides via $PORT env var; 10000 is Render's standard)
ENV PORT=10000

# Static EXPOSE (env vars don't resolve in EXPOSE instruction)
EXPOSE 10000

# Health check -- verify nginx is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
