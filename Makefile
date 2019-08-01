.PHONY: itest install utest

lextest: install
	sylva lex examples/hello.sy

parsetest: install
	sylva parse examples/hello.sy

utest: install
	@echo "No testing framework set up yet"

install:
	python setup.py install

