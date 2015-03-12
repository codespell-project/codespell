prefix ?= /usr/local
bindir ?= ${prefix}/bin
datadir ?= ${prefix}/share/codespell

_VERSION := $(shell grep -e "VERSION = '[0-9]\.[0-9]" codespell.py | cut -f 3 -d ' ')
VERSION = $(subst ',,$(_VERSION))

PHONY = all check clean install git-tag-release

all: codespell

codespell: codespell.py
	sed "s|^default_dictionary = .*|default_dictionary = '${datadir}/dictionary.txt'|" < $^ > $@

check:
	test 1bfb1f089c3c7772f0898f66df089b9e = $$(./codespell.py example/ | md5sum | cut -f1 -d\ )

install: codespell
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
	github-release release --repo codespell --tag v$(VERSION) --name v$(VERSION)
	github-release upload  --repo codespell --tag v$(VERSION) \
		--name codespell-$(VERSION).tar.xz \
		--file codespell-$(VERSION).tar.xz
	github-release upload  --repo codespell --tag v$(VERSION) \
		--name codespell-$(VERSION).tar.xz.asc \
		--file codespell-$(VERSION).tar.xz.asc

clean:
	rm -rf codespell
