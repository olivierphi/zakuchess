PYTHON_VERSION ?= 3.13
PYTHON_BIN ?= ./.venv/bin
PYTHON ?= ${PYTHON_BIN}/python
UV ?= bin/uv
DJANGO_SETTINGS_MODULE ?= project.settings.development
SUB_MAKE = ${MAKE} --no-print-directory

.DEFAULT_GOAL := help

.PHONY: help
help:
# @link https://github.com/marmelab/javascript-boilerplate/blob/master/makefile
	@grep -P '^[a-zA-Z/_.-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: uv_sync_opts ?= --all-extras
install: bin/uv .venv .env.local ## Install the Python dependencies, via `uv sync`
# Install Python dependencies:
	${UV} sync ${uv_sync_opts}
# Install pre-commit hooks:
	${PYTHON_BIN}/pre-commit install
# Create a shim for Black (actually using Ruff), so the IDE can use it:
	@${SUB_MAKE} .venv/bin/black

.PHONY: dev
dev: address ?= zakuchess.localhost
dev: port ?= 8000
dev: dotenv_file ?= .env.local
dev: .venv .env.local db.sqlite3 ## Start the Django development server
	@${SUB_MAKE} django/manage cmd='runserver ${address}:${port}'

.PHONY: test
test: dotenv_file ?= .env.local
test: pytest_opts ?=
test: .env.local ## Launch the pytest tests suite
	@${PYTHON_BIN}/dotenv -f '${dotenv_file}' run -- \
		${PYTHON_BIN}/pytest ${pytest_opts}

.PHONY: code-quality/all
code-quality/all: code-quality/ruff_format code-quality/ruff_lint code-quality/mypy  ## Run all our code quality tools

.PHONY: code-quality/ruff_format
code-quality/ruff_format: ruff_opts ?=
code-quality/ruff_format: ## Automated 'a la Prettier' code formatting
# @link https://docs.astral.sh/ruff/formatter/
	@${PYTHON_BIN}/ruff format ${ruff_opts} src/

.PHONY: code-quality/ruff_lint
code-quality/ruff_lint: ruff_opts ?= --fix
code-quality/ruff_lint: ## Fast linting
# @link https://docs.astral.sh/ruff/linter/
	@${PYTHON_BIN}/ruff check src/ ${ruff_opts}

.PHONY: code-quality/mypy
code-quality/mypy: mypy_opts ?=
code-quality/mypy: ## Python's equivalent of TypeScript
# @link https://mypy.readthedocs.io/en/stable/
	@${PYTHON_BIN}/mypy src/ ${mypy_opts}
	
.PHONY: django/manage
django/manage: env_vars ?=
django/manage: dotenv_file ?= .env.local
django/manage: cmd ?= --help
django/manage: .venv .env.local ## Run a Django management command
	@echo "Running Django management command: ${cmd}"
	@DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} ${env_vars} \
			${PYTHON_BIN}/dotenv -f '${dotenv_file}' run -- \
					${PYTHON} manage.py ${cmd}

.PHONY: django/createsuperuser
django/createsuperuser: username ?= admin@zakuchess.localhost
django/createsuperuser: email ?= admin@zakuchess.localhost
django/createsuperuser: password ?= localdev
django/createsuperuser: ## Create a superuser for local development
	@${SUB_MAKE} django/manage \
		cmd='createsuperuser --noinput --username ${username} --email ${email}' \
		env_vars='DJANGO_SUPERUSER_PASSWORD=${password}'
	@echo "Superuser created: ${username} / ${password}"

bin/uv: uv_version ?= 0.8.17
bin/uv: # Install `uv` and `uvx` locally in the "bin/" folder
	curl -LsSf "https://astral.sh/uv/${uv_version}/install.sh" | \
		UV_INSTALL_DIR="$$(pwd)/bin" UV_NO_MODIFY_PATH=1 sh
	@echo "We'll use 'bin/uv' to manage Python dependencies." 

.venv: ## Initialises the Python virtual environment in a ".venv" folder, via uv
	@${UV} venv

.env.local: ## Copies the ".env.sample" file to ".env.local" (git-ignored)
	cp .env.sample .env.local

db.sqlite3: dotenv_file ?= .env.local
db.sqlite3: .env.local ## Initialises the SQLite database
	touch db.sqlite3
	@${SUB_MAKE} django/manage cmd='migrate'
	@DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}

data/pypi-data/serials.json:
	## Downloads the serials.json file listing PyPI's _last-serial data for each package
	@curl -L https://raw.githubusercontent.com/pypi-data/pypi-json-data/refs/heads/main/release_data/serials.json \
		> data/pypi-data/serials.json

data/pypi-data/dump.sqlite3:
	## Downloads the SQLite database from "https://github.com/pypi-data/pypi-json-data"
	@curl -L https://github.com/pypi-data/pypi-json-data/releases/download/latest/pypi-data.sqlite.gz \
		| gzip -d \
		> data/pypi-data/dump.sqlite3

.PHONY: fetch-pypi-data
fetch-pypi-data: data/pypi-data/serials.json data/pypi-data/dump.sqlite3

.venv/bin/black: .venv ## A simple and stupid shim to use the IDE's Black integration with Ruff
	@echo '#!/usr/bin/env sh\n$$(dirname "$$0")/ruff format $$@' > ${PYTHON_BIN}/black
	@chmod +x ${PYTHON_BIN}/black
