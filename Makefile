NODE_BIN = ./node_modules/.bin
SUB_MAKE = ${MAKE} --no-print-directory

.DEFAULT_GOAL := help

help:
# @link https://github.com/marmelab/javascript-boilerplate/blob/master/makefile
	@grep -P '^[a-zA-Z/_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ./node_modules ## Install the dependencies and some code quality tools


.PHONY: dev
dev: .env.local
dev: ## Start Hono in "development" mode, as well as our frontend assets compilers in "watch" mode
	@./node_modules/.bin/concurrently --names "hono,css,js" --prefix-colors "blue,yellow,green" \
		"${SUB_MAKE} backend/watch" \
		"${SUB_MAKE} frontend/watch"

# Here starts the backend stuff

.PHONY: backend/watch
backend/watch: host ?= localhost
backend/watch: port ?= 3000
backend/watch: dotenv_file ?= .env.local
backend/watch: ## Start the Hono development server
	@SERVER_HOST=${address} SERVER_PORT=${port} NODE_ENV=development \
		${NODE_BIN}/dotenv -e ${dotenv_file} \
			${NODE_BIN}/tsx -r dotenv/config \
				watch --clear-screen=false \
				src/server-nodejs.ts \
			| ${NODE_BIN}/pino-pretty

.PHONY: assets/download-and-copy
assets/download-and-copy:
	${NODE_BIN}/tsx scripts/assets-download-and-copy.ts

# Here starts the frontend stuff

.PHONY: frontend/watch
frontend/watch: ## Compile the JS assets via Vite, in 'watch & development' mode
	@${NODE_BIN}/vite --strictPort --mode development 

.PHONY: frontend/build
frontend/build: ## Compile the JS assets via Vite,
	@${NODE_BIN}/vite build --mode production 


# Production-related stuff

build: ## Build the production assets
	@${NODE_BIN}/vite build --mode production


# Here starts the "misc util targets" stuff


.PHONY: code-quality/all
code-quality/all: code-quality/lint code-quality/format code-quality/ts  ## Run all our code quality tools

.PHONY: code-quality/lint
code-quality/lint: lint_opts ?=
code-quality/lint: ## Runs ESLint
	@${NODE_BIN}/eslint ${lint_ops} src/

.PHONY: code-quality/format
code-quality/format: format_opts ?= --write
code-quality/format: ## Runs Prettier
	@${NODE_BIN}/prettier ${format_opts} src/

.PHONY: code-quality/ts
code-quality/ts: ts_opts ?=
code-quality/ts: ## Runs a TypeScript check pass
	@${NODE_BIN}/tsc --noEmit ${ts_opts}

.env.local:
	cp .env.dist .env.local


# Here starts Docker-related stuff

DOCKER_IMG_NAME ?= zakuchess
DOCKER_TAG ?= latest

.PHONY: docker/build
docker/build: use_buildkit ?= 1 # @link https://docs.docker.com/develop/develop-images/build_enhancements/
docker/build: docker_build_args ?=
docker/build: ## Docker: build the image
	DOCKER_BUILDKIT=${use_buildkit} docker build -t ${DOCKER_IMG_NAME}:${DOCKER_TAG} ${docker_build_args} .
	

.PHONY: docker/local/run
docker/local/run: port ?= 3000
docker/local/run: port_exposed ?= 3000
docker/local/run: docker_args ?= --rm -it
docker/local/run: docker_env ?= -e NODE_ENV=production
docker/local/run: cmd ?= node_modules/.bin/tsx src/server-nodejs.ts
docker/local/run: user_id ?= $$(id -u)
docker/local/run: ## Docker: launch the previously built image, listening on port 8080
	docker run -p ${port_exposed}:${port} -v "${PWD}/.docker/:/app/shared_volume/" \
		-u ${user_id} \
		${docker_env} ${docker_args} \
		${DOCKER_IMG_NAME}:${DOCKER_TAG} \
		${cmd}


.PHONY: docker/local/shell
docker/local/shell: docker_args ?= --rm -it
docker/local/shell: docker_env ?= -e NODE_ENV=production
docker/local/shell: cmd ?= bash
docker/local/shell: user_id ?= $$(id -u)
docker/local/shell:
	docker run -v "${PWD}/.docker/:/app/shared_volume/" \
		-u ${user_id} \
		${docker_env} ${docker_args} \
		-e DJANGO_SETTINGS_MODULE=project.settings.production \
		${DOCKER_IMG_NAME}:${DOCKER_TAG} \
		${cmd}
