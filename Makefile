SORT_ARGS := -f -b

DICTIONARIES := codespell_lib/data/dictionary*.txt

PHONY := all check check-dictionary sort-dictionary trim-dictionary clean

all: check-dictionary codespell.1

codespell.1: codespell.1.include bin/codespell
	PYTHONPATH=. help2man ./bin/codespell --include codespell.1.include --no-info --output codespell.1
	sed -i '/\.SS \"Usage/,+2d' codespell.1

check-dictionary:
	@for dictionary in ${DICTIONARIES}; do \
		if ! LC_ALL=C sort ${SORT_ARGS} -c $$dictionary; then \
			echo "Dictionary $$dictionary not sorted. Sort with 'make sort-dictionary'"; \
			exit 1; \
		fi; \
		if egrep -n "^\s*$$|\s$$|^\s" $$dictionary; then \
			echo "Dictionary $$dictionary contains leading/trailing whitespace and/or blank lines.  Trim with 'make trim-dictionary'"; \
			exit 1; \
		fi; \
	done
	@if command -v pytest4 > /dev/null; then \
		pytest codespell_lib/tests/test_dictionary.py; \
	fi

sort-dictionary:
	@for dictionary in ${DICTIONARIES}; do \
		LC_ALL=C sort ${SORT_ARGS} -u -o $$dictionary $$dictionary; \
	done

trim-dictionary:
	@for dictionary in ${DICTIONARIES}; do \
		sed -E -i.bak -e 's/^[[:space:]]+//; s/[[:space:]]+$$//; /^$$/d' $$dictionary && rm $$dictionary.bak; \
	done

pypi:
	python setup.py sdist register upload

clean:
	rm -rf codespell.1
