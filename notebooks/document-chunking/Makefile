NBTEST = ../../bin/nbtest
NOTEBOOKS = \
	with-index-pipelines.ipynb \
	with-langchain-splitters.ipynb

.PHONY: all $(NOTEBOOKS)

all: $(NOTEBOOKS)

$(NOTEBOOKS):
	-$(NBTEST) $@
