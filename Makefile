.PHONY: install test lextest parsetest utest docs

help:
	@echo "Commands: install | test | lextest | parsetest | utest | docs"

venv:
ifeq ($(VIRTUAL_ENV), )
	$(error "Not running in a virtualenv")
endif

depinstall: venv
	@pip install -r dev-requirements.txt

install: depinstall
	python setup.py install

test: install
	sylva examples/hello.sy

lextest: install
	sylva --only-lex stdlib/libc.sy stdlib/sys.sy

parsetest: install
	sylva --only-parse stdlib/libc.sy stdlib/sys.sy

utest: install
	@echo "No testing framework set up yet"

docs:
	@dox doc
