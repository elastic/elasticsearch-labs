.PHONY: pre-commit test nbtest notebooks

pre-commit:
	python -m venv .venv
	.venv/bin/pip install -r requirements-dev.txt
	.venv/bin/pre-commit install

all: test

test: nbtest notebooks

nbtest:
	$(MAKE) -C test/nbtest

notebooks: search document-chunking

search:
	$(MAKE) -C notebooks/search

document-chunking:
	$(MAKE) -C notebooks/document-chunking
