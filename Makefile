prefix ?= /usr
bindir ?= ${prefix}/bin
datadir ?= ${prefix}/share/codesell

_VERSION := $(shell grep -e "VERSION = '[0-9]\.[0-9]" codespell.py | cut -f 3 -d ' ')
VERSION = $(subst ',,$(_VERSION))

PHONY = all install git-tag-release

all:
	@echo "Use 'make install' setting prefix and DESTDIR as desired"
	@echo "E.g.: make prefix=/usr/local DESTDIR=/tmp/test-inst install"

install:
	install -d ${DESTDIR}${datadir} ${DESTDIR}${bindir}
	install -m644 -t ${DESTDIR}${datadir} data/dictionary.txt data/linux-kernel.exclude
	install -m755 -t ${DESTDIR}${bindir} codespell.py

git-tag-release:
	git commit -a -m "codespell $(VERSION)"
	git tag -m "codespell $(VERSION)" -s v$(VERSION)
	git gc --prune=0

codespell-$(VERSION).tar.xz.asc: codespell-$(VERSION).tar.xz
	gpg --armor --detach-sign --output codespell-$(VERSION).tar.xz.asc codespell-$(VERSION).tar.xz

codespell-$(VERSION).tar.xz:
	git archive --format=tar --prefix codespell-$(VERSION)/ v$(VERSION) | xz > codespell-$(VERSION).tar.xz

tar-sync: codespell-$(VERSION).tar.xz codespell-$(VERSION).tar.xz.asc
	scp $^ packages.profusion.mobi:/var/www/packages/codespell/
