SORT_ARGS := -f -b

DICTIONARIES := codespell_lib/data/dictionary*.txt

PHONY := all check check-dictionaries sort-dictionaries trim-dictionaries check-dictionary sort-dictionary trim-dictionary clean

all: check-dictionaries codespell.1

check-dictionary: check-dictionaries
sort-dictionary: sort-dictionaries
trim-dictionary: trim-dictionaries

codespell.1: codespell.1.include bin/codespell
	PYTHONPATH=. help2man ./bin/codespell --include codespell.1.include --no-info --output codespell.1
	sed -i '/\.SS \"Usage/,+2d' codespell.1

check-dictionaries:
	@for dictionary in ${DICTIONARIES}; do \
		if ! LC_ALL=C sort ${SORT_ARGS} -c $$dictionary; then \
			echo "Dictionary $$dictionary not sorted. Sort with 'make sort-dictionaries'"; \
			exit 1; \
		fi; \
		if egrep -n "^\s*$$|\s$$|^\s" $$dictionary; then \
			echo "Dictionary $$dictionary contains leading/trailing whitespace and/or blank lines.  Trim with 'make trim-dictionaries'"; \
			exit 1; \
		fi; \
	done
	@if command -v pytest > /dev/null; then \
		pytest codespell_lib/tests/test_dictionary.py; \
	else \
		echo "Test dependencies not present, install using 'pip install -e \".[dev]\"'"; \
		exit 1; \
	fi

sort-dictionaries:
	@for dictionary in ${DICTIONARIES}; do \
		LC_ALL=C sort ${SORT_ARGS} -u -o $$dictionary $$dictionary; \
	done

trim-dictionaries:
	@for dictionary in ${DICTIONARIES}; do \
		sed -E -i.bak -e 's/^[[:space:]]+//; s/[[:space:]]+$$//; /^$$/d' $$dictionary && rm $$dictionary.bak; \
	done

check-manifest:
	check-manifest

pypi:
	python setup.py sdist register upload

clean:
	rm -rf codespell.1
