UTILS_NODE_BIN ?= ./node_modules/.bin
FRONTEND_DIR ?= ./frontend
BACKEND_DIR ?= ./backend
FRONTEND_NODE_BIN ?= ${FRONTEND_DIR}/node_modules/.bin
BACKEND_NODE_BIN ?= ${BACKEND_DIR}/node_modules/.bin
SUB_MAKE = ${MAKE} --no-print-directory

.DEFAULT_GOAL := help

help:
# @link https://github.com/marmelab/javascript-boilerplate/blob/master/makefile
	@grep -P '^[.a-zA-Z/_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: node_modules/ frontend/node_modules/ backend/node_modules/ shared/node_modules/ .env.local ## Install the "shared", backend and frontend dependencies

.PHONY: dev
dev: ## Starts Astro and Hono, both in "developement" mode
	@${UTILS_NODE_BIN}/concurrently --names "hono,astro" --prefix-colors "yellow,green" \
		"${SUB_MAKE} backend/dev" \
		"${SUB_MAKE} frontend/dev" \

.PHONY: prod
prod: frontend/node_modules/ backend/node_modules/ ## Builds the frontend, then starts Hono in "production" mode
	${SUB_MAKE} frontend/build
	${SUB_MAKE} backend/prod

.PHONY: code-quality/all
code-quality/all: code-quality/oxlint code-quality/prettier code-quality/frontend/tsc code-quality/backend/tsc ## Run all our code quality tools

.PHONY: code-quality/oxlint
code-quality/oxlint: ## Run linter
	@${UTILS_NODE_BIN}/oxlint

.PHONY: code-quality/prettier
code-quality/prettier: ## Run Prettier
	@${UTILS_NODE_BIN}/prettier --write frontend/ backend/

.PHONY: code-quality/frontend/tsc
code-quality/frontend/tsc: ## Run a TypeScript check on the frontend code
	@cd ${FRONTEND_DIR} && ./node_modules/.bin/tsc --noEmit

.PHONY: code-quality/backend/tsc
code-quality/backend/tsc: ## Run a TypeScript check on the backend code
	@cd ${BACKEND_DIR} && ./node_modules/.bin/tsc --noEmit

.PHONY: backend/dev
backend/dev: check/node
	@cd ${BACKEND_DIR} && \
		node \
			--watch \
			--env-file-if-exists=../.env.dist \
			src/server-nodejs.ts

.PHONY: backend/prod
backend/prod: node_env ?= production
backend/prod: cookie_signing_secret_key ?= not-a-secret-but-that-s-not-a-problem
backend/prod: backend/node_modules/
	@cd ${BACKEND_DIR} && \
		NODE_ENV=${node_env} COOKIES_SIGNING_SECRET=${cookie_signing_secret_key} node \
			src/server-nodejs.ts

.PHONY: frontend/dev
frontend/dev: check/node frontend/node_modules/
	@cd ${FRONTEND_DIR} && ./node_modules/.bin/astro dev

.PHONY: frontend/build
frontend/build: check/node
	@cd ${FRONTEND_DIR} && ./node_modules/.bin/astro build

# Here starts the "misc util targets" stuff

node_modules/: check/node
	@npm install

frontend/node_modules/: check/node
	@cd frontend/ && npm install

backend/node_modules/: check/node
	@cd backend/ && npm install

shared/node_modules/: check/node
	@cd shared/ && npm install

.PHONY: check/node
# Check Node.js version (must be 24.x)
check/node:
	@if command -v node > /dev/null; then \
		node_ver=$$(node -v | cut -d'v' -f2); \
		if ! echo "$$node_ver" | grep -q "^24\."; then \
			echo "✗ Error: Node.js version $$node_ver found, but version 24.x is required"; \
			exit 1; \
		fi \
	else \
		echo "✗ Error: Node.js is not installed"; \
		exit 1; \
	fi
