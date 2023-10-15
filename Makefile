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
		"${SUB_MAKE} frontend/css/watch" \
		"${SUB_MAKE} frontend/js/watch"

# Here starts the backend stuff

.PHONY: backend/watch
backend/watch: host ?= localhost
backend/watch: port ?= 3000
backend/watch: dotenv_file ?= .env.local
backend/watch: ## Start the Hono development server
	@SERVER_HOST=${address} SERVER_PORT=${port} ${NODE_BIN}/tsx watch src/index.tsx

.PHONY: download_assets
download_assets:
	${NODE_BIN}/tsx scripts/download-assets.ts

# Here starts the frontend stuff

.PHONY: frontend/watch
frontend/watch: ## Compile the CSS & JS assets of our various Django apps, in 'watch' mode
	@.${NODE_BIN}/concurrently --names "css,js" --prefix-colors "yellow,green" \
		"${SUB_MAKE} frontend/css/watch" \
		"${SUB_MAKE} frontend/js/watch"

.PHONY: frontend/css/watch
frontend/css/watch: ## Compile the CSS assets of our various Django apps, in 'watch' mode
	@${SUB_MAKE} frontend/css/compile \
		tailwind_compile_opts='--watch' sass_compile_opts='--watch'

.PHONY: frontend/css/compile
frontend/css/compile:
	@${NODE_BIN}/concurrently --names "tailwind" \
		"${SUB_MAKE} frontend/css/compile/tailwind"

frontend/css/compile/tailwind: tailwind_compile_opts ?=
frontend/css/compile/tailwind: ## Compile the Tailwind CSS assets from our Components' classes
	@${NODE_BIN}/tailwind ${tailwind_compile_opts} \
		-i ./static-src/css/tailwind.css \
		-o ./static/css/tailwind.css

.PHONY: frontend/js/watch
frontend/js/watch: ## Compile the JS assets of our various Django apps, in 'watch' mode
#@${SUB_MAKE} frontend/js/compile esbuild_compile_opts='--watch'

.PHONY: frontend/js/compile
frontend/js/compile: js_webui_src ?= src/apps/webui/static-src/webui/ts
frontend/js/compile: js_webui_dest ?= src/apps/webui/static/webui/js
frontend/js/compile: js_chess_src ?= src/apps/chess/static-src/chess/ts
frontend/js/compile: js_chess_dest ?= src/apps/chess/static/chess/js
frontend/js/compile: ## Compile the JS assets of our various Django apps
	@${NODE_BIN}/concurrently --names "webui,chess" \
		"${SUB_MAKE} frontend/js/compile_app_files src='${js_webui_src}/main.ts' dest=${js_webui_dest}" \
		"${SUB_MAKE} frontend/js/compile_app_files src='${js_chess_src}/chess-main.ts' dest=${js_chess_dest}"

.PHONY: frontend/js/compile_app_files
frontend/js/compile_app_files: esbuild_compile_opts ?=
frontend/js/compile_app_files:
	@${NODE_BIN}/esbuild ${esbuild_compile_opts} \
		${src} \
		--bundle --sourcemap --target=chrome58,firefox57,safari11,edge16 \
		--outdir="${dest}"

# Here starts the "misc util targets" stuff

.env.local:
	cp .env.dist .env.local
