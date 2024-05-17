#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see
# https://www.gnu.org/licenses/old-licenses/gpl-2.0.html.
"""
Copyright (C) 2010-2011  Lucas De Marchi <lucas.de.marchi@gmail.com>
Copyright (C) 2011  ProFUSION embedded systems
"""

from typing import (
    Container,
    Dict,
    Optional,
    Sequence,
)

# Pass all misspellings through this translation table to generate
# alternative misspellings and fixes.
alt_chars = (("'", "’"),)  # noqa: RUF001


class Misspelling:
    def __init__(self, candidates: Sequence[str], fix: bool, reason: str) -> None:
        self.candidates = candidates
        self.fix = fix
        self.reason = reason


class Spellchecker:
    def __init__(self) -> None:
        self._misspellings: Dict[str, Misspelling] = {}

    def check_lower_cased_word(self, word: str) -> Optional[Misspelling]:
        """Check a given word against the loaded dictionaries

        :param word: The word to check. This should be all lower-case.
        """
        return self._misspellings.get(word)

    def add_from_file(
        self,
        filename: str,
        *,
        ignore_words: Container[str] = frozenset(),
    ) -> None:
        """Parse a codespell dictionary

        :param filename: The codespell dictionary file to parse
        :param ignore_words: Words to ignore from this dictionary.
        """
        misspellings = self._misspellings
        with open(filename, encoding="utf-8") as f:
            translate_tables = [(x, str.maketrans(x, y)) for x, y in alt_chars]
            for line in f:
                [key, data] = line.split("->")
                # TODO: For now, convert both to lower.
                #       Someday we can maybe add support for fixing caps.
                key = key.lower()
                data = data.lower()
                if key not in ignore_words:
                    _add_misspelling(key, data, misspellings)
                # generate alternative misspellings/fixes
                for x, table in translate_tables:
                    if x in key:
                        alt_key = key.translate(table)
                        alt_data = data.translate(table)
                        if alt_key not in ignore_words:
                            _add_misspelling(alt_key, alt_data, misspellings)


def _add_misspelling(
    key: str,
    data: str,
    misspellings: Dict[str, Misspelling],
) -> None:
    data = data.strip()

    if "," in data:
        fix = False
        data, reason = data.rsplit(",", 1)
        reason = reason.lstrip()
    else:
        fix = True
        reason = ""

    misspellings[key] = Misspelling(
        tuple(c.strip() for c in data.split(",")),
        fix,
        reason,
    )
