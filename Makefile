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
	sylva --output-folder sbuild/ examples/hello.sy

.PHONY: parsetest

parsetest: dev-install ## Run parser tests
	sylva --output-folder sbuild/ --only-parse examples/hello.sy

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
