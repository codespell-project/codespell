SORT_ARGS := -f -b

DICTIONARY := codespell_lib/data/dictionary.txt

PHONY := all check check-dictionary sort-dictionary trim-dictionary clean

all: check-dictionary codespell.1

codespell.1: codespell.1.include bin/codespell
	PYTHONPATH=. help2man ./bin/codespell --include codespell.1.include --no-info --output codespell.1
	sed -i '/\.SS \"Usage/,+2d' codespell.1

check-dictionary:
	@if ! LC_ALL=C sort ${SORT_ARGS} -c ${DICTIONARY}; then \
		echo "Dictionary not sorted. Sort with 'make sort-dictionary'"; \
		exit 1; \
	fi
	@if egrep -n "^\s*$$|\s$$|^\s" ${DICTIONARY}; then \
		echo "Dictionary contains leading/trailing whitespace and/or blank lines.  Trim with 'make trim-dictionary'"; \
		exit 1; \
	fi
	@if command -v pytest > /dev/null; then \
		pytest codespell_lib/tests/test_dictionary.py; \
	fi

sort-dictionary:
	LC_ALL=C sort ${SORT_ARGS} -u -o ${DICTIONARY} ${DICTIONARY}

trim-dictionary:
	sed -E -i.bak -e 's/^[[:space:]]+//; s/[[:space:]]+$$//; /^$$/d' ${DICTIONARY} && rm ${DICTIONARY}.bak

pypi:
	python setup.py sdist register upload

clean:
	rm -rf codespell.1
