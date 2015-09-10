prefix ?= /usr/local
bindir ?= ${prefix}/bin
datadir ?= ${prefix}/share/codespell
mandir ?= ${prefix}/share/man/man1

_VERSION := $(shell grep -e "VERSION = '[0-9]\.[0-9]" codespell.py | cut -f 3 -d ' ')
VERSION = $(subst ',,$(_VERSION))

SORT_ARGS := -f

PHONY := all manpage check check-dictionary sort-dictionary install git-tag-release tar-sync clean

all: codespell manpage

codespell: codespell.py check-dictionary
	sed "s|^default_dictionary = .*|default_dictionary = '${datadir}/dictionary.txt'|" < $< > $@
	chmod 755 codespell

manpage: codespell codespell.1.include
	help2man ./codespell --include codespell.1.include --no-info --output codespell.1
	sed -i '/\.SS \"Usage/,+2d' codespell.1
	gzip -9 -f codespell.1

check:
	test 1bfb1f089c3c7772f0898f66df089b9e = $$(./codespell.py example/ | md5sum | cut -f1 -d\ )

check-dictionary:
	@if ! LANG=C sort ${SORT_ARGS} -c data/dictionary.txt; then \
		echo "Dictionary not sorted. Sort with 'make sort-dictionary'"; \
		exit 1; \
	fi

sort-dictionary:
	LANG=C sort ${SORT_ARGS} -u -o data/dictionary.txt data/dictionary.txt

install: codespell manpage
	install -d ${DESTDIR}${datadir} ${DESTDIR}${bindir} ${DESTDIR}${mandir}
	install -m644 -t ${DESTDIR}${datadir} data/dictionary.txt data/linux-kernel.exclude
	install -m755 -T codespell ${DESTDIR}${bindir}/codespell
	install -d ${DESTDIR}${mandir}
	install -m644 -t ${DESTDIR}${mandir} codespell.1.gz

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
	rm -rf codespell.1
	rm -rf codespell.1.gz
