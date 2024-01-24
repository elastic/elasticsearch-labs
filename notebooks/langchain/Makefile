NBTEST = ../../bin/nbtest
NOTEBOOKS = \
	langchain-using-own-model.ipynb

.PHONY: all $(NOTEBOOKS)

all: $(NOTEBOOKS)

$(NOTEBOOKS):
	-$(NBTEST) $@
