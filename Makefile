PYTHON_BIN ?= ./.venv/bin
NODE_BIN ?= ./node_modules/.bin
PYTHON ?= ${PYTHON_BIN}/python
UV ?= ./bin/uv
SUB_MAKE = ${MAKE} --no-print-directory

.DEFAULT_GOAL := help

help:
# @link https://github.com/marmelab/javascript-boilerplate/blob/master/makefile
	@grep -P '^[.a-zA-Z/_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: bin/uv .venv node_modules/ .env.local ## Install the Python and frontend dependencies
	${SUB_MAKE} backend/install
	${PYTHON_BIN}/pre-commit install

.PHONY: dev
dev: ## Starts Astro and FastAPI, both in "developement" mode
	@${NODE_BIN}/concurrently --names "fastapi,astro" --prefix-colors "yellow,green" \
		"${SUB_MAKE} backend/dev" \
		"${SUB_MAKE} frontend/dev" \

.PHONY: prod
prod: bin/uv .venv node_modules/ backend/install ## Builds the frontend, then starts FastAPI in "production" mode
	${SUB_MAKE} frontend/build
	${SUB_MAKE} backend/prod

.PHONY: code-quality/all
code-quality/all: code-quality/backend/ruff_format code-quality/backend/ruff_lint code-quality/backend/mypy  ## Run all our code quality tools

.PHONY: code-quality/backend/ruff_format
code-quality/backend/ruff_format: ruff_opts ?=
code-quality/backend/ruff_format: ## Automated 'a la Prettier' code formatting
# @link https://docs.astral.sh/ruff/formatter/
	@${PYTHON_BIN}/ruff format ${ruff_opts} src-backend/

.PHONY: code-quality/backend/ruff_lint
code-quality/backend/ruff_lint: ruff_opts ?= --fix
code-quality/backend/ruff_lint: ## Fast linting
# @link https://docs.astral.sh/ruff/linter/
	@${PYTHON_BIN}/ruff check src-backend/ ${ruff_opts}

.PHONY: code-quality/backend/mypy
code-quality/backend/mypy: mypy_opts ?=
code-quality/backend/mypy: ## Python's equivalent of TypeScript
# @link https://mypy.readthedocs.io/en/stable/
	@${PYTHON_BIN}/mypy src-backend/ ${mypy_opts}

.PHONY: backend/install
backend/install:
	@${UV} sync --all-extras

.PHONY: backend/dev
backend/dev: backend/install
	@${PYTHON_BIN}/uvicorn \
		--env-file .env.local \
		--reload \
		--reload-dir src-backend/zakuchess \
		--app-dir src-backend/ \
		zakuchess.app:app

.PHONY: backend/prod
backend/prod: backend/install
	@${PYTHON_BIN}/uvicorn \
		--app-dir src-backend/ \
		zakuchess.app:app

.PHONY: frontend/dev
frontend/dev: check/node
	@node --run dev

.PHONY: frontend/lint
frontend/lint: check/node
	@./node_modules/.bin/oxlint src-frontend

.PHONY: frontend/build
frontend/build: check/node
	@${NODE_BIN}/astro build

# Here starts the "misc util targets" stuff

bin/uv: uv_version ?= 0.8.14
bin/uv: # Install `uv` and `uvx` locally in the "bin/" folder
	curl -LsSf "https://astral.sh/uv/${uv_version}/install.sh" | \
		CARGO_DIST_FORCE_INSTALL_DIR="$$(pwd)/bin" INSTALLER_NO_MODIFY_PATH=1 sh
	@echo "We'll use 'bin/uv' to manage Python dependencies."

.venv: ## Initialises the Python virtual environment in a ".venv" folder, via uv
	bin/uv venv

.env.local:
	cp .env.dist .env.local

node_modules/:
	npm install

.venv/bin/black: .venv ## A simple and stupid shim to use the IDE's Black integration with Ruff
	@echo '#!/usr/bin/env sh\n$$(dirname "$$0")/ruff format $$@' > ${PYTHON_BIN}/black
	@chmod +x ${PYTHON_BIN}/black

.PHONY: check/node
# Check Node.js version (must be 22.x)
check/node:
	@if command -v node > /dev/null; then \
		node_ver=$$(node -v | cut -d'v' -f2); \
		if ! echo "$$node_ver" | grep -q "^22\."; then \
			echo "✗ Error: Node.js version $$node_ver found, but version 22.x is required"; \
			exit 1; \
		fi \
	else \
		echo "✗ Error: Node.js is not installed"; \
		exit 1; \
	fi
