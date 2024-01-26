.PHONY: install pre-commit nbtest test notebooks

test: nbtest notebooks

notebooks: search document-chunking model-upgrades langchain

search:
	$(MAKE) -C notebooks/search

document-chunking:
	$(MAKE) -C notebooks/document-chunking

model-upgrades:
	$(MAKE) -C notebooks/model-upgrades

langchain:
	$(MAKE) -C notebooks/langchain

install: pre-commit nbtest

pre-commit:
	python -m venv .venv
	.venv/bin/pip install -r requirements-dev.txt
	.venv/bin/pre-commit install

nbtest:
	python3 -m venv .venv
	.venv/bin/pip install elastic-nbtest
