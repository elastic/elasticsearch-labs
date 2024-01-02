NBTEST = ../../bin/nbtest
NOTEBOOKS = \
	00-quick-start.ipynb \
	01-keyword-querying-filtering.ipynb \
	02-hybrid-search.ipynb \
	03-ELSER.ipynb \
	04-multilingual.ipynb \
	05-query-rules.ipynb \
	06-synonyms-api.ipynb

.PHONY: all $(NOTEBOOKS)

all: $(NOTEBOOKS)

$(NOTEBOOKS):
	-$(NBTEST) $@
