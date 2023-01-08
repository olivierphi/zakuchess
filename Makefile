NODE_BIN ?= ./node_modules/.bin

.PHONY: code-quality
code-quality: code-quality/prettier code-quality/ts-check

.PHONY: code-quality/prettier
code-quality/prettier: prettier_opts ?= --write
code-quality/prettier:
	${NODE_BIN}/prettier ${prettier_opts} src/

.PHONY: code-quality/ts-check
code-quality/ts-check: tsc_opts ?= -b
code-quality/ts-check:
	${NODE_BIN}/tsc ${tsc_opts}
