
#########################################################################
# Frontend stuff


# Frontend steps copy-pasted-and-adapted from:
# @link https://github.com/vercel/next.js/blob/canary/examples/with-docker-multi-env/docker/production/Dockerfile

# 1. Install dependencies only when needed
FROM node:16-alpine AS frontend_deps
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
FROM node:16-alpine AS frontend_build
RUN apk add --no-cache make
RUN mkdir -p /app
WORKDIR /app
COPY --from=frontend_deps /app/node_modules ./node_modules
COPY frontend-src ./frontend-src
COPY Makefile ./
RUN make frontend/js/compile frontend/css/compile

#########################################################################
# Backend stuff

FROM python:3.10 AS backend_build

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

RUN mkdir -p /app
WORKDIR /app

RUN python -m venv .venv

COPY pyproject.toml poetry.lock ./
RUN poetry install --without dev

FROM python:3.10-slim AS backend_run

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    libpq5 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app
WORKDIR /app

RUN addgroup -gid 1001 webapp
RUN useradd --gid 1001 --uid 1001 webapp
RUN chown -R 1001:1001 /app 
USER 1001:1001

COPY --chown=1001:1001 --from=frontend_build /app/frontend-out frontend-out
COPY --chown=1001:1001 --from=backend_build /app/.venv .venv
COPY --chown=1001:1001 . .

ENV PYTHONPATH=/app/src

RUN .venv/bin/python bin/scripts/download_assets.py
RUN cp -p -r frontend-src/js/bot frontend-out/js

RUN DJANGO_SETTINGS_MODULE=project.settings.docker_build \
    .venv/bin/python src/manage.py collectstatic --noinput

EXPOSE 8080

CMD [".venv/bin/gunicorn", "--bind", ":8080", "--workers", "2", "project.wsgi"]
