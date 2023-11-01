PYTHON_BINS ?= ./.venv/bin
PYTHON ?= ${PYTHON_BINS}/python
PYTHONPATH ?= ${PWD}/src
DJANGO_SETTINGS_MODULE ?= project.settings.development
SUB_MAKE = ${MAKE} --no-print-directory

.DEFAULT_GOAL := help

help:
# @link https://github.com/marmelab/javascript-boilerplate/blob/master/makefile
	@grep -P '^[a-zA-Z/_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: .venv ./node_modules ## Install the Python and frontend dependencies
	${PYTHON_BINS}/pre-commit install
	${PYTHON_BINS}/poetry install

.PHONY: dev
dev: .env.local db.sqlite3
dev: ## Start Django in "development" mode, as well as our frontend assets compilers in "watch" mode
	@./node_modules/.bin/concurrently --names "django,css,js" --prefix-colors "blue,yellow,green" \
		"${SUB_MAKE} backend/watch" \
		"${SUB_MAKE} frontend/css/watch" \
		"${SUB_MAKE} frontend/js/watch"

# Here starts the backend stuff

.PHONY: download_assets
download_assets: download_assets_opts ?=
download_assets:
	${PYTHON_BINS}/python scripts/download_assets.py ${download_assets_opts}

.PHONY: backend/watch
backend/watch: address ?= localhost
backend/watch: port ?= 8000
backend/watch: dotenv_file ?= .env.local
backend/watch: ## Start the Django development server
	@${SUB_MAKE} django/manage cmd='runserver ${address}:${port}'

.PHONY: backend/resetdb
backend/resetdb: dotenv_file ?= .env.local
backend/resetdb: # Destroys the SQLite database and recreates it from scratch
	rm -f db.sqlite3
	@${SUB_MAKE} db.sqlite3

.PHONY: backend/createsuperuser
backend/createsuperuser: dotenv_file ?= .env.local
backend/createsuperuser: email ?= admin@zakuchess.localhost
backend/createsuperuser: password ?= localdev
backend/createsuperuser: ## Creates a Django superuser for the development environment
	@${SUB_MAKE} django/manage cmd='createsuperuser --noinput' \
		env_vars='DJANGO_SUPERUSER_USERNAME=${email} DJANGO_SUPERUSER_EMAIL=${email} DJANGO_SUPERUSER_PASSWORD=${password}'
	@echo 'You can log in to http://localhost:8000/admin/ with the following credentials: ${email} / ${password}'

.PHONY: test
test: dotenv_file ?= .env.local
test: pytest_opts ?=
test: ## Launch the pytest tests suite
	@PYTHONPATH=${PYTHONPATH} \
		${PYTHON_BINS}/dotenv -f '${dotenv_file}' run -- \
		${PYTHON_BINS}/pytest ${pytest_opts}

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
code-quality/ruff: ruff_opts ?= --fix
code-quality/ruff: ## Fast linting
# @link https://mypy.readthedocs.io/en/stable/
	@PYTHONPATH=${PYTHONPATH} ${PYTHON_BINS}/ruff src/ ${ruff_opts}

.PHONY: code-quality/mypy
code-quality/mypy: mypy_opts ?=
code-quality/mypy: ## Python's equivalent of TypeScript
# @link https://mypy.readthedocs.io/en/stable/
	@PYTHONPATH=${PYTHONPATH} ${PYTHON_BINS}/mypy src/ ${mypy_opts}

# Here starts the frontend stuff

.PHONY: frontend/watch
frontend/watch: ## Compile the CSS & JS assets of our various Django apps, in 'watch' mode
	@./node_modules/.bin/concurrently --names "css,js" --prefix-colors "yellow,green" \
		"${SUB_MAKE} frontend/css/watch" \
		"${SUB_MAKE} frontend/js/watch"

.PHONY: frontend/css/watch
frontend/css/watch: ## Compile the CSS assets of our various Django apps, in 'watch' mode
	@${SUB_MAKE} frontend/css/compile \
		tailwind_compile_opts='--watch' sass_compile_opts='--watch'

.PHONY: frontend/css/compile
frontend/css/compile:
	@./node_modules/.bin/concurrently --names "tailwind" \
		"${SUB_MAKE} frontend/css/compile/tailwind"

frontend/css/compile/tailwind: tailwind_compile_opts ?=
frontend/css/compile/tailwind: ## Compile the Tailwind CSS assets of our various Django apps
	@./node_modules/.bin/tailwind ${tailwind_compile_opts} \
		-i ./src/apps/webui/static-src/webui/css/tailwind.css \
		-o ./src/apps/webui/static/webui/css/tailwind.css

.PHONY: frontend/js/watch
frontend/js/watch: ## Compile the JS assets of our various Django apps, in 'watch' mode
	@${SUB_MAKE} frontend/js/compile esbuild_compile_opts='--watch'

.PHONY: frontend/js/compile
frontend/js/compile: js_webui_src ?= src/apps/webui/static-src/webui/ts
frontend/js/compile: js_webui_dest ?= src/apps/webui/static/webui/js
frontend/js/compile: js_chess_src ?= src/apps/chess/static-src/chess/ts
frontend/js/compile: js_chess_dest ?= src/apps/chess/static/chess/js
frontend/js/compile: ## Compile the JS assets of our various Django apps
	@./node_modules/.bin/concurrently --names "webui,chess" \
		"${SUB_MAKE} frontend/js/compile_app_files src='${js_webui_src}/main.ts' dest=${js_webui_dest}" \
		"${SUB_MAKE} frontend/js/compile_app_files src='${js_chess_src}/chess-main.ts' dest=${js_chess_dest}"

.PHONY: frontend/js/compile_app_files
frontend/js/compile_app_files: esbuild_compile_opts ?=
frontend/js/compile_app_files:
	@./node_modules/.bin/esbuild ${esbuild_compile_opts} \
		${src} \
		--bundle --sourcemap --target=chrome58,firefox57,safari11,edge16 \
		--outdir="${dest}"

# Here starts the "misc util targets" stuff

.venv: poetry_version ?= 1.6.0
.venv: ## Initialises the Python virtual environment in a ".venv" folder
	python -m venv .venv
	${PYTHON_BINS}/pip install -U pip poetry==${poetry_version}

.env.local:
	cp .env.dist .env.local

db.sqlite3: dotenv_file ?= .env.local
db.sqlite3: ## Initialises the SQLite database
	touch db.sqlite3
	@${SUB_MAKE} django/manage cmd='migrate'
	@PYTHONPATH=${PYTHONPATH} DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} \
		${PYTHON_BINS}/dotenv -f '${dotenv_file}' run -- \
		${PYTHON_BINS}/python scripts/optimise_db.py

django/manage: env_vars ?= 
django/manage: dotenv_file ?= .env.local
django/manage: cmd ?= --help
django/manage: .venv .env.local ## Run a Django management command
	@DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} ${env_vars} \
		${PYTHON_BINS}/dotenv -f '${dotenv_file}' run -- \
		${PYTHON} src/manage.py ${cmd}

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
docker/local/run: docker_args ?= --rm -it
docker/local/run: docker_env ?= -e SECRET_KEY=does-not-matter-here -e DATABASE_URL=sqlite:////app/shared_volume/db.sqlite3 -e ALLOWED_HOSTS=* -e SECURE_SSL_REDIRECT=
docker/local/run: cmd ?= scripts/start_server.sh
docker/local/run: GUNICORN_CMD_ARGS ?= --bind :8080 --workers 2 --max-requests 120 --max-requests-jitter 20 --timeout 8
docker/local/run: user_id ?= $$(id -u)
docker/local/run: ## Docker: launch the previously built image, listening on port 8080
	docker run -p ${port_exposed}:${port} -v "${PWD}/.docker/:/app/shared_volume/" \
		-u ${user_id} \
		${docker_env} ${docker_args} \
		-e DJANGO_SETTINGS_MODULE=project.settings.production \
		-e GUNICORN_CMD_ARGS='${GUNICORN_CMD_ARGS}' \
		${DOCKER_IMG_NAME}:${DOCKER_TAG} \
		${cmd}

.PHONY: docker/local/shell
docker/local/shell: docker_args ?= --rm -it
docker/local/shell: docker_env ?= -e SECRET_KEY=does-not-matter-here -e DATABASE_URL=sqlite:////app/shared_volume/db.sqlite3 -e ALLOWED_HOSTS=* -e SECURE_SSL_REDIRECT=
docker/local/shell: cmd ?= bash
docker/local/shell: user_id ?= $$(id -u)
docker/local/shell:
	docker run -v "${PWD}/.docker/:/app/shared_volume/" \
		-u ${user_id} \
		${docker_env} ${docker_args} \
		-e DJANGO_SETTINGS_MODULE=project.settings.production \
		${DOCKER_IMG_NAME}:${DOCKER_TAG} \
		${cmd}

.PHONY: docker/local/migrate
docker/local/migrate:
	${SUB_MAKE} docker/local/shell \
		cmd='/app/.venv/bin/python src/manage.py migrate'

# Here starts Fly.io-related stuff
.PHONY: fly.io/deploy
fly.io/deploy: deploy_build_args ?= 
fly.io/deploy: version ?= $$(date --iso-8601)::$$(git rev-parse --short HEAD)
fly.io/deploy: ## Fly.io: deploy the previously built Docker image
	@echo "Deploying version '${version}'..."
	flyctl deploy ${deploy_build_args} \
		--env ZAKUCHESS_VERSION="${version}"
		
.PHONY: fly.io/db/local_backup
fly.io/db/local_backup: backup_name ?= $$(date --iso-8601)
fly.io/db/local_backup: ## Fly.io: backup the SQLite database locally
	@flyctl ssh sftp get /zakuchess_sqlite_dbs/zakuchess.dev.sqlite3
	@mv zakuchess.dev.sqlite3 "zakuchess.prod.backup.${backup_name}.sqlite3"
	@echo "Saved to 'zakuchess.prod.backup.${backup_name}.sqlite3'"

.PHONY: fly.io/ssh
fly.io/ssh: ## Fly.io: start a SSH session within our app
	flyctl ssh console
