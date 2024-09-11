
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
COPY src/apps/daily_challenge/components ./src/apps/daily_challenge/components
COPY src/apps/webui/components ./src/apps/webui/components
# We're going to use our Makefile to build the assets:
COPY Makefile ./
# ..and use the Tailwind config file:
COPY tailwind.config.js ./

# Right, let's build our app's assets!
RUN make frontend/img frontend/js/compile frontend/css/compile \
    esbuild_compile_opts='--minify' \
    tailwind_compile_opts='--minify'

#########################################################################
# Backend stuff
# Large chunks copy-pasted from https://hynek.me/articles/docker-uv/ :-)

FROM python:3.11-slim-bookworm AS backend_build

# The following does not work in Podman unless you build in Docker
# compatibility mode: <https://github.com/containers/podman/issues/8477>
# You can manually prepend every RUN script with `set -ex` too.
SHELL ["sh", "-exc"]

RUN <<EOT
apt-get update -qy
apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    build-essential \
    ca-certificates \
    curl
EOT

# Install uv.
# https://docs.astral.sh/uv/guides/integration/docker/
COPY --from=ghcr.io/astral-sh/uv:0.4.9 /uv /usr/local/bin/uv

RUN mkdir -p /app
WORKDIR /app

# - Silence uv complaining about not being able to use hard links,
# - tell uv to byte-compile packages for faster application startups,
# - prevent uv from accidentally downloading isolated Python builds,
# - pick a Python,
# - and finally declare `/app/.venv` as the target for `uv sync`.
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.11 \
    UV_PROJECT_ENVIRONMENT=/app/.venv
    
# Prepare a virtual environment.
# This is cached until the Python version changes above.
RUN --mount=type=cache,target=/root/.cache \
    uv venv $UV_PROJECT_ENVIRONMENT

# Synchronize DEPENDENCIES without the application itself.
# This layer is cached until uv.lock or pyproject.toml change.
# Since there's no point in shipping lock files, we move them
# into a directory that is NOT copied into the runtime image.
COPY pyproject.toml /_lock/
COPY uv.lock /_lock/
RUN --mount=type=cache,target=/root/.cache <<EOT
cd /_lock
uv sync \
    --frozen \
    --no-dev \
    --no-install-project
EOT

    
FROM python:3.11-slim-bookworm AS assets_download

# By having a separate build stage for downloading assets, we can cache them
# as long as the `download_assets.py` doesn't change.

# should preferably be the same as in `uv.lock`:
ENV PYTHON_HTTPX_VERSION=0.27.2

RUN pip install -U pip httpx==${PYTHON_HTTPX_VERSION}

RUN mkdir -p /app
WORKDIR /app

COPY scripts/download_assets.py scripts/download_assets.py

RUN python scripts/download_assets.py

FROM python:3.11-slim-bookworm AS backend_run

SHELL ["sh", "-exc"]

# Add the application virtualenv to search path.
ENV PATH=/app/.venv/bin:$PATH

# Allow our "src/" folder to be seen as a package root:
ENV PYTHONPATH=/app/src

# Let's make sure that our Django app sees "/app" as its base dir, rather than
# a resolved symlink in the venv. This is important for the collectstatic command.
ENV DJANGO_BASE_DIR=/app

# Don't run our app as root.
RUN <<EOT
groupadd --gid 1001 app
useradd --uid 1001 -g app -N app -d /app
EOT

USER app
WORKDIR /app

COPY --chown=1001:1001 scripts scripts
COPY --chown=1001:1001 Makefile pyproject.toml manage.py LICENSE ./
COPY --chown=1001:1001 src src

COPY --chown=1001:1001 --from=frontend_build /app/src/apps/webui/static src/apps/webui/static
COPY --chown=1001:1001 --from=frontend_build /app/src/apps/chess/static src/apps/chess/static

COPY --chown=1001:1001 --from=backend_build /app/.venv .venv

COPY --chown=1001:1001 --from=assets_download /app/src/apps/webui/static/webui/fonts/OpenSans.woff2 src/apps/webui/static/webui/fonts/OpenSans.woff2
COPY --chown=1001:1001 --from=assets_download /app/src/apps/chess/static/chess/js/bot src/apps/chess/static/chess/js/bot
COPY --chown=1001:1001 --from=assets_download /app/src/apps/chess/static/chess/units src/apps/chess/static/chess/units
COPY --chown=1001:1001 --from=assets_download /app/src/apps/chess/static/chess/symbols src/apps/chess/static/chess/symbols

RUN python -V
RUN python -Im site
# Smoke test:
RUN DJANGO_SETTINGS_MODULE=project.settings.docker_build \
    .venv/bin/python manage.py shell -c "from apps.daily_challenge.models import DailyChallenge"

# Collect static files.
RUN DJANGO_SETTINGS_MODULE=project.settings.docker_build \
    .venv/bin/python manage.py collectstatic --noinput

# Ok, let's get ready to run that server!
EXPOSE 8080

ENV DJANGO_SETTINGS_MODULE=project.settings.production

ENV GUNICORN_CMD_ARGS="--bind 0.0.0.0:8080 --workers 4 -k uvicorn_worker.UvicornWorker --max-requests 120 --max-requests-jitter 20 --timeout 8"

RUN chmod +x scripts/start_server.sh
# See <https://hynek.me/articles/docker-signals/>.
STOPSIGNAL SIGINT
ENTRYPOINT ["scripts/start_server.sh"]
