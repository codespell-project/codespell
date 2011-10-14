
prefix ?= /usr
bindir ?= ${prefix}/bin
datadir ?= ${prefix}/share/codespell

all:
	@echo "Use 'make install' setting prefix and DESTDIR as desired"
	@echo "E.g.: make prefix=/usr/local DESTDIR=/tmp/test-inst install"

install:
	install -d ${DESTDIR}${datadir} ${DESTDIR}${bindir}
	install -m644 -t ${DESTDIR}${datadir} data/dictionary.txt data/linux-kernel.exclude
	install -m755 -t ${DESTDIR}${bindir} codespell.py
