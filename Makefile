SHELL:=/bin/sh

.PHONY: test

test: install ## Build hello world example
	sylva --output-folder sbuild/ examples/hello.sy

.PHONY: venv

venv:
ifeq ($(VIRTUAL_ENV), )
	$(error "Not running in a virtualenv")
endif

.PHONY: depinstall

depinstall: venv ## Install dependencies
	@pip install -r dev-requirements.txt

.PHONY: install

install: depinstall ## Install
	@pip install .

.PHONY: parsetest

parsetest: install ## Run parser tests
	sylva --output-folder sbuild/ --only-parse examples/hello.sy

.PHONY: utest

utest: install ## Run unit tests
	@echo "No testing framework set up yet"

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
