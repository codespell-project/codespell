SORT_ARGS := -f

PHONY := all check check-dictionary sort-dictionary clean

all: check-dictionary codespell.1

codespell.1: codespell.1.include bin/codespell
	PYTHONPATH=. help2man ./bin/codespell --include codespell.1.include --no-info --output codespell.1
	sed -i '/\.SS \"Usage/,+2d' codespell.1

check-dictionary:
	@if ! LC_ALL=C sort ${SORT_ARGS} -c codespell_lib/data/dictionary.txt; then \
		echo "Dictionary not sorted. Sort with 'make sort-dictionary'"; \
		exit 1; \
	fi

sort-dictionary:
	LC_ALL=C sort ${SORT_ARGS} -u -o codespell_lib/data/dictionary.txt codespell_lib/data/dictionary.txt

pypi:
	python setup.py sdist register upload

clean:
	rm -rf codespell.1
