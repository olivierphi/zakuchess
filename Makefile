PYTHON_BINS ?= ./.venv/bin
PYTHON ?= ${PYTHON_BINS}/python
DJANGO_SETTINGS_MODULE ?= project.settings.development
SUB_MAKE = ${MAKE} --no-print-directory
UV ?= bin/uv

.DEFAULT_GOAL := help

help:
# @link https://github.com/marmelab/javascript-boilerplate/blob/master/makefile
	@grep -P '^[.a-zA-Z/_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: backend/install frontend/install ## Install the Python and frontend dependencies
	

.PHONY: dev
dev: .env.local db.sqlite3
dev: ## Start Django in "development" mode, as well as our frontend assets compilers in "watch" mode
	@${SUB_MAKE} frontend/img
	@./node_modules/.bin/concurrently --names "django,css,js" --prefix-colors "blue,yellow,green" \
		"${SUB_MAKE} backend/watch" \
		"${SUB_MAKE} frontend/css/watch" \
		"${SUB_MAKE} frontend/js/watch"

# Here starts the backend stuff

.PHONY: download_assets
download_assets: download_assets_opts ?=
download_assets:
	${PYTHON_BINS}/python scripts/download_assets.py ${download_assets_opts}

.PHONY: backend/install
backend/install: uv_sync_opts ?= --all-extras --no-build
backend/install: bin/uv .venv ## Install the Python dependencies (via uv) and install pre-commit
	${UV} sync ${uv_sync_opts}
	${PYTHON_BINS}/pre-commit install
	@${SUB_MAKE} .venv/bin/black

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
	@${PYTHON_BINS}/dotenv -f '${dotenv_file}' run -- \
		${PYTHON_BINS}/pytest ${pytest_opts}

.PHONY: code-quality/all
code-quality/all: code-quality/ruff_check code-quality/ruff_lint code-quality/mypy  ## Run all our code quality tools

.PHONY: code-quality/ruff_check
code-quality/ruff_check: ruff_opts ?=
code-quality/ruff_check: ## Automated 'a la Prettier' code formatting
# @link https://docs.astral.sh/ruff/formatter/
	@${PYTHON_BINS}/ruff format ${ruff_opts} src/

.PHONY: code-quality/ruff_lint
code-quality/ruff_lint: ruff_opts ?= --fix
code-quality/ruff_lint: ## Fast linting
# @link https://docs.astral.sh/ruff/linter/
	@${PYTHON_BINS}/ruff check src/ ${ruff_opts}

.PHONY: code-quality/mypy
code-quality/mypy: mypy_opts ?=
code-quality/mypy: ## Python's equivalent of TypeScript
# @link https://mypy.readthedocs.io/en/stable/
	@${PYTHON_BINS}/mypy src/ ${mypy_opts}

# Here starts the frontend stuff

.PHONY: frontend/install
frontend/install: ## Install the frontend dependencies (via npm)
	npm install

.PHONY: frontend/watch
frontend/watch: ./node_modules ## Compile the CSS & JS assets of our various Django apps, in 'watch' mode
	@./node_modules/.bin/concurrently --names "img,css,js" --prefix-colors "yellow,green" \
		"${SUB_MAKE} frontend/img" \
		"${SUB_MAKE} frontend/css/watch" \
		"${SUB_MAKE} frontend/js/watch"

.PHONY: frontend/img
frontend/img: ## Copy some assets from the apps' "static-src" folders to their "static" ones
## No 'watch' mode on this at the moment... 
	@${SUB_MAKE} frontend/img/copy_assets

.PHONY: frontend/css/watch
frontend/css/watch: ## Compile the CSS assets of our various Django apps, in 'watch' mode
	@${SUB_MAKE} frontend/css/compile \
		tailwind_compile_opts='--watch'

.PHONY: frontend/css/compile
frontend/css/compile:
	@./node_modules/.bin/concurrently --names "tailwind" \
		"${SUB_MAKE} frontend/css/compile/tailwind"

frontend/css/compile/tailwind: tailwind_compile_opts ?=
frontend/css/compile/tailwind: ## Compile the Tailwind-based stylesheet
	@./node_modules/.bin/tailwind ${tailwind_compile_opts} \
		-i ./src/apps/webui/static-src/webui/css/zakuchess.css \
		-o ./src/apps/webui/static/webui/css/zakuchess.css

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
		--bundle --sourcemap --target=chrome87,firefox78,safari14,edge88 \
		--outdir="${dest}"

.PHONY: frontend/img/copy_assets
frontend/img/copy_assets: img_chess_src ?= src/apps/chess/static-src/chess/img
frontend/img/copy_assets: img_chess_dest ?= src/apps/chess/static/chess
frontend/img/copy_assets:
	@mkdir -p '${img_chess_dest}'
	@cp -r -p '${img_chess_src}' '${img_chess_dest}'
	@echo "Copied image assets from Django apps' 'static-src' to 'static' folders."

# Here starts the "misc util targets" stuff

bin/uv: uv_version ?= 0.4.4
bin/uv: # Install `uv` and `uvx` locally in the "bin/" folder
	curl -LsSf "https://astral.sh/uv/${uv_version}/install.sh" | \
		CARGO_DIST_FORCE_INSTALL_DIR="$$(pwd)" INSTALLER_NO_MODIFY_PATH=1 sh
	@echo "We'll use 'bin/uv' to manage Python dependencies." 

.venv: ## Initialises the Python virtual environment in a ".venv" folder, via uv
	${UV} venv

.env.local:
	cp .env.dist .env.local

.venv/bin/black: .venv ## A simple and stupid shim to use the IDE's Black integration with Ruff
	@echo '#!/usr/bin/env sh\n$$(dirname "$$0")/ruff format $$@' > ${PYTHON_BINS}/black
	@chmod +x ${PYTHON_BINS}/black

db.sqlite3: dotenv_file ?= .env.local
db.sqlite3: ## Initialises the SQLite database
	touch db.sqlite3
	@${SUB_MAKE} django/manage cmd='migrate'
	@DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} \
		${PYTHON_BINS}/dotenv -f '${dotenv_file}' run -- \
		${PYTHON_BINS}/python scripts/optimise_db.py

django/manage: env_vars ?= 
django/manage: dotenv_file ?= .env.local
django/manage: cmd ?= --help
django/manage: .venv .env.local ## Run a Django management command
	@DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} ${env_vars} \
		${PYTHON_BINS}/dotenv -f '${dotenv_file}' run -- \
		${PYTHON} manage.py ${cmd}

./.venv/bin/django: .venv install

./node_modules: frontend/install


# Here starts the "Lichess database" stuff

data/lichess_db_puzzle.csv: ## Download the Lichess puzzles database (CSV format)
	@curl 'https://database.lichess.org/lichess_db_puzzle.csv.zst' \
		| zstd -d > data/lichess_db_puzzle.csv

data/lichess_db_puzzle.sqlite3: batch_size ?= 1000
data/lichess_db_puzzle.sqlite3: sqlite_utils_ops ?=
data/lichess_db_puzzle.sqlite3: data/lichess_db_puzzle.csv ## Convert the Lichess puzzles database into a SQLite database
# @link https://sqlite-utils.datasette.io/en/stable/cli.html#inserting-csv-or-tsv-data
# N.B. use `make data/lichess_db_puzzle.csv sqlite_utils_ops='--stop-after 50'` for quick tests 
	@rm -f data/puzzles.sqlite3
	@${PYTHON_BINS}/sqlite-utils create-database data/lichess_db_puzzle.sqlite3 --enable-wal
	@${PYTHON_BINS}/sqlite-utils insert data/lichess_db_puzzle.sqlite3 puzzles data/lichess_db_puzzle.csv \
		--csv --detect-types --pk PuzzleId --batch-size ${batch_size} \
		${sqlite_utils_ops}
	@${PYTHON_BINS}/sqlite-utils create-index data/lichess_db_puzzle.sqlite3 puzzles \
		PuzzleId Rating Popularity NbPlays
	@${SUB_MAKE} data/lichess_db_puzzle.sqlite3/stats

.PHONY: data/lichess_db_puzzle.sqlite3/stats
data/lichess_db_puzzle.sqlite3/stats:
	@${PYTHON_BINS}/sqlite-utils query data/lichess_db_puzzle.sqlite3 \
		'select count(*) as puzzles_count from puzzles' --csv
	@${PYTHON_BINS}/sqlite-utils query data/lichess_db_puzzle.sqlite3 \
		'select avg(Rating), avg(Popularity) from puzzles' --csv

# Here starts Load tesing-related stuff

load_testing/locust: processes_count ?= 8
load_testing/locust: ## Start a load testing session, powered by Locust
	@${PYTHON_BINS}/locust \
		--web-host 127.0.0.1 \
		--processes ${processes_count}


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
docker/local/shell: docker_args ?= --rm -it --user app
docker/local/shell: docker_env ?= -e SECRET_KEY=does-not-matter-here -e DATABASE_URL=sqlite:////app/shared_volume/db.sqlite3 -e ALLOWED_HOSTS=* -e SECURE_SSL_REDIRECT=
docker/local/shell: cmd ?= bash
docker/local/shell: user_id ?= $$(id -u)
docker/local/shell:
	docker run -v "${PWD}/.docker/:/app/shared_volume/" \
		-u ${user_id} \
		${docker_env} ${docker_args} \
		-e DJANGO_SETTINGS_MODULE=project.settings.production \
		--entrypoint ${cmd} \
		${DOCKER_IMG_NAME}:${DOCKER_TAG}

.PHONY: docker/local/migrate
docker/local/migrate:
	${SUB_MAKE} docker/local/shell \
		cmd='/app/.venv/bin/python manage.py migrate'

# Here starts Fly.io-related stuff
.PHONY: fly.io/deploy
fly.io/deploy: deploy_build_args ?= 
fly.io/deploy: version ?= $$(date --iso-8601)::$$(git rev-parse --short HEAD)
fly.io/deploy: ## Fly.io: deploy the previously built Docker image
	@echo "Deploying version '${version}'..."
	flyctl deploy ${deploy_build_args} \
		--env ZAKUCHESS_VERSION="${version}"
		
.PHONY: fly.io/db/local_backup
fly.io/db/local_backup: backup_name ?= $$(date --iso-8601=seconds | cut -d + -f 1)
fly.io/db/local_backup: ## Fly.io: backup the SQLite database locally
	@flyctl ssh sftp get /zakuchess_sqlite_dbs/zakuchess.dev.sqlite3
	@mv zakuchess.dev.sqlite3 "zakuchess.prod.backup.${backup_name}.sqlite3"
	@echo "Saved to 'zakuchess.prod.backup.${backup_name}.sqlite3'"
		
.PHONY: fly.io/db/prod_to_local
fly.io/db/prod_to_local: local_db ?= ./db.sqlite3
fly.io/db/prod_to_local: backup_name ?= ./db.local.backup.$$(date --iso-8601=seconds | cut -d + -f 1).sqlite3
fly.io/db/prod_to_local: ## Fly.io: replace our local SQLite database with the one from the prod environment
	@mv "${local_db}" "${backup_name}"
	@flyctl ssh sftp get /zakuchess_sqlite_dbs/zakuchess.dev.sqlite3
	@mv zakuchess.dev.sqlite3 "${local_db}"
	@echo "Replaced local DB with a copy from the production DB. The previous local DB has been saved as '${backup_name}'."

.PHONY: fly.io/ssh
fly.io/ssh: ## Fly.io: start a SSH session within our app
	flyctl ssh console
