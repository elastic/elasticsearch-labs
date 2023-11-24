.PHONY: test nbtest notebooks

test: nbtest notebooks

nbtest:
	$(MAKE) -C test/nbtest

notebooks: search document-chunking

search:
	$(MAKE) -C notebooks/search

document-chunking:
	$(MAKE) -C notebooks/document-chunking