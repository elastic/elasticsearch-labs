# this is the list of notebooks that are integrated with the testing framework
NOTEBOOKS = $(shell bin/find-notebooks-to-test.sh)
VENV = .venv

.PHONY: install install-pre-commit install-nbtest test notebooks

test: install-nbtest notebooks

notebooks:
	bin/nbtest $(NOTEBOOKS)

pre-commit: install-pre-commit
	$(VENV)/bin/pre-commit run --all-files

install: install-pre-commit install-nbtest

install-pre-commit:
	python -m venv $(VENV)
	$(VENV)/bin/pip install -qqq -r requirements-dev.txt
	$(VENV)/bin/pre-commit install

install-nbtest:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -qqq elastic-nbtest
