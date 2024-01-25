NBTEST = ../../bin/nbtest
NOTEBOOKS = \
	langchain-using-own-model.ipynb \
	langchain-vector-store-using-elser.ipynb

.PHONY: all $(NOTEBOOKS)

all: $(NOTEBOOKS)

$(NOTEBOOKS):
	-$(NBTEST) $@
