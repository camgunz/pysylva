SHELL:=/bin/bash

.PHONY: venv

venv:
ifeq ($(VIRTUAL_ENV), )
	$(error "Not running in a virtualenv")
endif

.PHONY: install

install: ## Install
	@pip install .

.PHONY: dev-install

dev-install: venv ## Install dependencies
	@pip install . .[dev]

.PHONY: test

test: dev-install ## Test hello world example
	@PYTHONPATH=. python -m sylva.cli \
		hello \
		--cpp=/usr/bin/clang \
		--libclang=/Library/Developer/CommandLineTools/usr/lib/libclang.dylib \
		--output-folder sbuild

.PHONY: parsetest

parsetest: ## Run parser tests
	@PYTHONPATH=. python -m sylva.cli \
		hello \
		--cpp=/usr/bin/clang \
		--libclang=/Library/Developer/CommandLineTools/usr/lib/libclang.dylib \
		--output-folder sbuild \
		--only-parse

.PHONY: utest

utest: dev-install ## Run unit tests
	@echo "No unit testing framework set up yet"

.PHONY: docs

docs: ## Build documentation
	@dox doc

.PHONY: parser

parser: ## Build parser
	@cd lark && make clean && make install

.PHONY: help

help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage: make [command] \n\nCommands: \n\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  %-15s %s\n", $$1, $$2 } /^##@/ { printf "\n%s\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo
