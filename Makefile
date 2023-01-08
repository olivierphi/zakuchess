NODE_BIN ?= ./node_modules/.bin
DATABASE_URL ?= postgresql://root@127.0.0.1:26257/defaultdb?sslmode=disable

.PHONY: code-quality
code-quality: code-quality/prettier code-quality/lint code-quality/ts-check

.PHONY: code-quality/prettier
code-quality/prettier: prettier_opts ?= --write  --list-different
code-quality/prettier:
	${NODE_BIN}/prettier ${prettier_opts} src/

.PHONY: code-quality/lint
code-quality/lint:
	${NODE_BIN}/next lint

.PHONY: code-quality/ts-check
code-quality/ts-check: tsc_opts ?= -b
code-quality/ts-check:
	${NODE_BIN}/tsc ${tsc_opts}

.PHONY: dev/repl
dev/repl: tsx_opts ?=
dev/repl:
	DATABASE_URL=${DATABASE_URL} ${NODE_BIN}/tsx ${tsx_opts}

.PHONY: db/cli
db/cli: host ?= db:26257
db/cli:
	HOST=${host} docker compose run --rm db-cli

.PHONY: db/migration/migrate/latest
db/migration/migrate/latest:
	DATABASE_URL=${DATABASE_URL} ${NODE_BIN}/knex migrate:latest \
		--knexfile ./bin/_knexfile.js

.PHONY: db/migration/migrate/reset
db/migration/migrate/reset:
	DATABASE_URL=${DATABASE_URL} ${NODE_BIN}/knex migrate:rollback --all \
		--knexfile ./bin/_knexfile.js

.PHONY: db/migration/create
db/migration/create: migration_name ?=
db/migration/create:
	DATABASE_URL=${DATABASE_URL} ${NODE_BIN}/knex migrate:make \
		--knexfile ./bin/_knexfile.js \
		${migration_name}
