prefix ?= /usr/local
bindir ?= ${prefix}/bin
datadir ?= ${prefix}/share/codespell

_VERSION := $(shell grep -e "VERSION = '[0-9]\.[0-9]" codespell.py | cut -f 3 -d ' ')
VERSION = $(subst ',,$(_VERSION))

PHONY = all check install git-tag-release

all: codespell

codespell: codespell.py
	sed "s|^default_dictionary = .*|default_dictionary = '${datadir}/dictionary.txt'|" < $^ > $@

check:
	test f66431c66b437c78523bc07b872b9a7b = $$(./codespell.py example/ | md5sum | cut -f1 -d\ )

install:
	install -d ${DESTDIR}${datadir} ${DESTDIR}${bindir}
	install -m644 -t ${DESTDIR}${datadir} data/dictionary.txt data/linux-kernel.exclude
	install -m755 -T codespell ${DESTDIR}${bindir}/codespell

git-tag-release:
	git commit -a -m "codespell $(VERSION)"
	git tag -m "codespell $(VERSION)" -s v$(VERSION)
	git gc --prune=0

codespell-$(VERSION).tar.xz.asc: codespell-$(VERSION).tar.xz
	gpg --armor --detach-sign --output $@ $^

codespell-$(VERSION).tar.xz:
	git archive --format=tar --prefix codespell-$(VERSION)/ v$(VERSION) | xz > $@

tar-sync: codespell-$(VERSION).tar.xz codespell-$(VERSION).tar.xz.asc
	scp $^ packages.profusion.mobi:/var/www/packages/codespell/
