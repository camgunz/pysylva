.PHONY: itest install utest

test: install
	sylva examples/hello.sy

lextest: install
	sylva --only-lex examples/hello.sy

parsetest: install
	sylva --only-parse examples/hello.sy

utest: install
	@echo "No testing framework set up yet"

install:
	python setup.py install

