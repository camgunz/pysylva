.PHONY: install test lextest parsetest utest

help:
	@echo "Commands: install | test | lextest | parsetest | utest"

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
	sylva --only-lex stdlib/os.sy stdlib/sys.sy

parsetest: install
	sylva --only-parse stdlib/sys.sy

utest: install
	@echo "No testing framework set up yet"
