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

.PHONY: dev
dev:
	@./node_modules/.bin/concurrently --names "django,css,js" --prefix-colors "blue,yellow,green" \
		"${MAKE} --no-print-directory backend/watch" \
		"${MAKE} --no-print-directory frontend/css/watch" \
		"${MAKE} --no-print-directory frontend/js/watch"

.PHONY: backend/watch
backend/watch: address ?= 127.0.0.1
backend/watch: port ?= 8000
backend/watch: ## Start the Django development server
	@PYTHONPATH=${PYTHONPATH} DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} \
		${PYTHON} src/manage.py runserver ${address}:${port}

.PHONY: test
test: pytest_opts ?=
test: ## Launch the pytest tests suite
	@PYTHONPATH=${PYTHONPATH} ${PYTHON_BINS}/pytest ${pytest_opts}

.PHONY: code-quality/all
code-quality/all: code-quality/black code-quality/djlint code-quality/isort code-quality/ruff code-quality/mypy  ## Run all our code quality tools

.PHONY: code-quality/black
code-quality/black: black_opts ?=
code-quality/black: ## Automated 'a la Prettier' code formatting
# @link https://black.readthedocs.io/en/stable/
	@${PYTHON_BINS}/black ${black_opts} src/ tests/

.PHONY: code-quality/djlint
code-quality/djlint: djlint_opts ?= --reformat
code-quality/djlint: ## Automated 'a la Prettier' code formatting for Jinja templates
# @link https://black.readthedocs.io/en/stable/
	@${PYTHON_BINS}/djlint src/ --extension=.tpl.html ${djlint_opts}

.PHONY: code-quality/isort
code-quality/isort: isort_opts ?=
code-quality/isort: ## Automated Python imports formatting
	@${PYTHON_BINS}/isort --settings-file=pyproject.toml ${isort_opts} src/ tests/

.PHONY: code-quality/ruff
code-quality/ruff: ruff_opts ?= --fix
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

.venv: ## Initialises the Python virtual environment in a ".venv" folder
	python -m venv .venv
	${PYTHON_BINS}/pip install -U pip poetry

./.venv/bin/django: .venv install

./node_modules: frontend/install

frontend/install:
	npm install

# Here starts Docker-related stuff

DOCKER_IMG_NAME ?= zakuchess
DOCKER_TAG ?= latest

.PHONY: docker/build
docker/build: use_buildkit ?= 1 # @link https://docs.docker.com/develop/develop-images/build_enhancements/
docker/build: docker_build_args ?=
docker/build: ## Docker: build the image
	DOCKER_BUILDKIT=${use_buildkit} docker build -t ${DOCKER_IMG_NAME}:${DOCKER_TAG} ${docker_build_args} .

.PHONY: docker/local/run
docker/local/run: port ?= 8080
docker/local/run: port_exposed ?= 8080
docker/local/run: docker_args ?= --rm
docker/local/run: docker_env ?= -e SECRET_KEY=does-not-matter-here -e DATABASE_URL=sqlite:////app/shared_volume/db.sqlite3 -e ALLOWED_HOSTS=* -e SECURE_SSL_REDIRECT=0
docker/local/run: cmd ?= /app/.venv/bin/gunicorn --bind 0.0.0.0:${port} --workers 2 project.wsgi
docker/local/run: user_id ?= $$(id -u)
docker/local/run: ## Docker: launch the previously built image, listening on port 8080
	docker run -p ${port_exposed}:${port} -v "${PWD}/.docker/:/app/shared_volume/" \
		-u ${user_id} \
		${docker_env} ${docker_args} \
		-e DJANGO_SETTINGS_MODULE=project.settings.production \
		${DOCKER_IMG_NAME}:${DOCKER_TAG} \
		${cmd}

.PHONY: docker/local/migrate
docker/local/migrate:
	${MAKE} --no-print-directory docker/local/run \
		cmd='/app/.venv/bin/python src/manage.py migrate'

# Here starts Fly.io-related stuff
.PHONY: fly.io/deploy
fly.io/deploy: deploy_build_args ?=
fly.io/deploy: ## Fly.io: deploy the previously built Docker image
	flyctl deploy ${deploy_build_args}

.PHONY: fly.io/ssh
fly.io/ssh: ## Fly.io: start a SSH session within our app
	flyctl ssh console
