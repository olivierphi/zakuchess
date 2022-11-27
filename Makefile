PYTHON_BINS ?= ./.venv/bin
PYTHON ?= ${PYTHON_BINS}/python
PYTHONPATH ?= ${PWD}/src
DJANGO_SETTINGS_MODULE ?= project.settings.development

.DEFAULT_GOAL := help

help:
# @link https://github.com/marmelab/javascript-boilerplate/blob/master/makefile
	@grep -P '^[a-zA-Z/_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: .venv ## Install the Python dependencies
	${PYTHON_BINS}/poetry install

dev: ## Start the Django development server
	@PYTHONPATH=${PYTHONPATH} DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} \
		${PYTHON} src/manage.py runserver

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


.venv: ## Initialises the Python virtual environment in a ".venv" folder
	python -m venv .venv
	${PYTHON_BINS}/pip install -U pip poetry

./.venv/bin/django: .venv install
