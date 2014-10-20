SELENA = bin/selena
BIN = $(SELENA)
BINDIR = /usr/bin

clean:
	rm -rf build dist *.egg-info *.pyc

install:
	install $(SELENA) $(BINDIR)
	python setup.py install

uninstall:
	rm  $(BINDIR)/$(SELENA)
	pip uninstall selena
