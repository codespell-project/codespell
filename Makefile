
prefix ?= /usr
bindir ?= ${prefix}/bin
datadir ?= ${prefix}/share/codespell


install:
	install -d ${DESTDIR}${datadir} ${DESTDIR}${bindir}
	install -m644 -t ${DESTDIR}${datadir} data/dictionary.txt data/linux-kernel.exclude
	install -m755 -t ${DESTDIR}${bindir} codespell.py
