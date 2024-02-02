# this is the list of notebooks that are integrated with the testing framework
NOTEBOOKS = $(shell bin/find-notebooks-to-test.sh)

.PHONY: install pre-commit nbtest test notebooks

test: nbtest notebooks

notebooks:
	bin/nbtest $(NOTEBOOKS)

install: pre-commit nbtest

pre-commit:
	python -m venv .venv
	.venv/bin/pip install -qqq -r requirements-dev.txt
	.venv/bin/pre-commit install

nbtest:
	python3 -m venv .venv
	.venv/bin/pip install -qqq elastic-nbtest
