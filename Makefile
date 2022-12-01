PYTHON_BINS ?= ./.venv/bin
PYTHON ?= ${PYTHON_BINS}/python
PYTHONPATH ?= ${PWD}/src
DJANGO_SETTINGS_MODULE ?= project.settings.development

.DEFAULT_GOAL := help

help:
# @link https://github.com/marmelab/javascript-boilerplate/blob/master/makefile
	@grep -P '^[a-zA-Z/_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: .venv ./node_modules ## Install the Python and frontend dependencies
	${PYTHON_BINS}/poetry install

dev: ## Start the Django development server
	@PYTHONPATH=${PYTHONPATH} DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} \
		${PYTHON} src/manage.py runserver 127.0.0.1:8000

.PHONY: test
test: pytest_opts ?=
test: ## Launch the pytest tests suite
	@PYTHONPATH=${PYTHONPATH} ${PYTHON_BINS}/pytest ${pytest_opts}

.PHONY: code-quality/all
code-quality/all: code-quality/black code-quality/isort code-quality/ruff code-quality/mypy  ## Run all our code quality tools

.PHONY: code-quality/black
code-quality/black: black_opts ?=
code-quality/black: ## Automated 'a la Prettier' code formatting
# @link https://black.readthedocs.io/en/stable/
	@${PYTHON_BINS}/black ${black_opts} src/ tests/

.PHONY: code-quality/isort
code-quality/isort: isort_opts ?=
code-quality/isort: ## Automated Python imports formatting
	@${PYTHON_BINS}/isort --settings-file=pyproject.toml ${isort_opts} src/ tests/

.PHONY: code-quality/ruff
code-quality/ruff: ruff_opts ?=
code-quality/ruff: ## Fast linting
# @link https://mypy.readthedocs.io/en/stable/
	@PYTHONPATH=${PYTHONPATH} ${PYTHON_BINS}/ruff src/ ${ruff_opts}

.PHONY: code-quality/mypy
code-quality/mypy: mypy_opts ?=
code-quality/mypy: ## Python's equivalent of TypeScript
# @link https://mypy.readthedocs.io/en/stable/
	@PYTHONPATH=${PYTHONPATH} ${PYTHON_BINS}/mypy src/ ${mypy_opts}

.PHONY: frontend/css/watch
frontend/css/watch:
	@${MAKE} --no-print-directory frontend/css/compile sass_compile_opts='--watch'

.PHONY: frontend/css/compile
frontend/css/compile: sass_compile_opts ?= 
frontend/css/compile:
	./node_modules/.bin/sass ${sass_compile_opts} \
		frontend-src/css/main.scss:frontend-out/css/main.css \
		frontend-src/css/chess-board.scss:frontend-out/css/chess-board.css \
		frontend-src/css/chess-units/theme/default.scss:frontend-out/css/chess-units/theme/default.css
		

.PHONY: frontend/js/watch
frontend/js/watch:
	@${MAKE} --no-print-directory frontend/js/compile esbuild_compile_opts='--watch'

.PHONY: frontend/watch
frontend/watch:
	@./node_modules/.bin/concurrently --names "css,js" --prefix-colors "yellow,green" \
		"${MAKE} --no-print-directory frontend/css/watch" \
		"${MAKE} --no-print-directory frontend/js/watch"

.PHONY: frontend/js/compile
frontend/js/compile: esbuild_compile_opts ?= 
frontend/js/compile:
	./node_modules/.bin/esbuild ${esbuild_compile_opts} \
		frontend-src/js/main.ts --bundle --outfile=frontend-out/js/main.js
# frontend-src/js/zakuchess-bot.js --bundle --outfile=frontend-out/js/zakuchess-bot.js 

.venv: ## Initialises the Python virtual environment in a ".venv" folder
	python -m venv .venv
	${PYTHON_BINS}/pip install -U pip poetry

./.venv/bin/django: .venv install

./node_modules: frontend/install

frontend/install:
	npm install
