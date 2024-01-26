NBTEST = ../../bin/nbtest
NOTEBOOKS = \
	tokenization.ipynb \
	with-index-pipelines.ipynb \
	with-langchain-splitters.ipynb

.PHONY: all $(NOTEBOOKS)

all: $(NOTEBOOKS)

$(NOTEBOOKS):
	-$(NBTEST) $@
