
#########################################################################
# Frontend stuff


# Frontend steps copy-pasted-and-adapted from:
# @link https://github.com/vercel/next.js/blob/canary/examples/with-docker-multi-env/docker/production/Dockerfile

# 1. Install dependencies only when needed
FROM node:18-alpine AS frontend_deps
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat

RUN mkdir -p /app
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
RUN \
  if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f pnpm-lock.yaml ]; then yarn global add pnpm && pnpm i; \
  else echo "Lockfile not found." && exit 1; \
  fi


# 2. Rebuild the source code only when needed
FROM node:18-alpine AS frontend_build
RUN apk add --no-cache make
RUN mkdir -p /app
WORKDIR /app

COPY --from=frontend_deps /app/node_modules ./node_modules

# Assets source: 
COPY src/lib/frontend-common ./src/lib/frontend-common
COPY src/apps/webui/static-src ./src/apps/webui/static-src
COPY src/apps/chess/static-src ./src/apps/chess/static-src
# We have to copy our components too, 
# so that Tailwind see the classes used in them:
COPY src/apps/chess/components ./src/apps/chess/components
COPY src/apps/webui/components ./src/apps/webui/components
# We're going to use our Makefile to build the assets:
COPY Makefile ./
# ..and use the Tailwind config file:
COPY tailwind.config.js ./

# Right, let's build our app's assets!
RUN make frontend/js/compile frontend/css/compile \
    esbuild_compile_opts='--minify' \
    tailwind_compile_opts='--minify'

#########################################################################
# Backend stuff

FROM python:3.11-slim-bookworm AS backend_build

ENV POETRY_VERSION=1.6.0

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=0 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install poetry==${POETRY_VERSION}

RUN mkdir -p /app
WORKDIR /app

RUN python -m venv --symlinks .venv

COPY pyproject.toml poetry.lock ./
RUN poetry install --only=main --no-root --no-interaction --no-ansi

FROM python:3.11-slim-bookworm AS assets_download

# By having a separate build stage for downloading assets, we can cache them
# as long as the `download_assets.py` doesn't change.

ENV PYTHON_REQUESTS_VERSION=2.31.0

RUN pip install -U pip requests==$PYTHON_REQUESTS_VERSION

RUN mkdir -p /app
WORKDIR /app

COPY scripts/download_assets.py scripts/download_assets.py

RUN python scripts/download_assets.py

FROM python:3.11-slim-bookworm AS backend_run

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=0 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libpq5 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app
WORKDIR /app

RUN addgroup -gid 1001 webapp
RUN useradd --gid 1001 --uid 1001 webapp
RUN chown -R 1001:1001 /app 

COPY --chown=1001:1001 scripts scripts
COPY --chown=1001:1001 src src

COPY --chown=1001:1001 --from=frontend_build /app/src/apps/webui/static src/apps/webui/static
COPY --chown=1001:1001 --from=frontend_build /app/src/apps/chess/static src/apps/chess/static

COPY --chown=1001:1001 --from=backend_build /app/.venv .venv

COPY --chown=1001:1001 --from=assets_download /app/src/apps/webui/static/webui/fonts/OpenSans.woff2 src/apps/webui/static/webui/fonts/OpenSans.woff2
COPY --chown=1001:1001 --from=assets_download /app/src/apps/chess/static/chess/js/bot src/apps/chess/static/chess/js/bot
COPY --chown=1001:1001 --from=assets_download /app/src/apps/chess/static/chess/units src/apps/chess/static/chess/units
COPY --chown=1001:1001 --from=assets_download /app/src/apps/chess/static/chess/symbols src/apps/chess/static/chess/symbols

COPY --chown=1001:1001 Makefile pyproject.toml LICENSE ./

ENV PATH="/app/.venv/bin:${PATH}"
RUN python -V

USER 1001:1001

ENV PYTHONPATH=/app/src

RUN DJANGO_SETTINGS_MODULE=project.settings.docker_build \
    .venv/bin/python src/manage.py collectstatic --noinput

EXPOSE 8080

ENV DJANGO_SETTINGS_MODULE=project.settings.production

ENV GUNICORN_CMD_ARGS="--bind :8080 --workers 2 --max-requests 120 --max-requests-jitter 20 --timeout 8"

RUN chmod +x scripts/start_server.sh
CMD ["scripts/start_server.sh"]
