.PHONY: test nbtest notebooks

test: nbtest notebooks search

nbtest:
	$(MAKE) -C test/nbtest

notebooks: search

search:
	$(MAKE) -C notebooks/search
