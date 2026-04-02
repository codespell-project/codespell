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


def is_camel_case_word(input_word: str) -> bool:
    return (
        (input_word != input_word.lower())
        and (input_word != input_word.upper())
        and ("_" not in input_word)
        and ("-" not in input_word)
        and (" " not in input_word)
    )


def is_camel_case_string(input_string: str) -> bool:
    return any(is_camel_case_word(word) for word in input_string.split(","))


def fix_case(word: str, fixword: str) -> str:
    if fixword == fixword.upper():
        # abbreviation, acronym: fixword is in all upper case.
        # Use fixword as per dictionary.
        # Eg. asscii->ASCII
        return fixword
    if word == word.capitalize() and fixword == fixword.lower():
        # word is capitalized and fixword(s) in lower.
        # Capitalize/Title fixword(s).
        # Eg. Weather, Whether,
        return fixword.title()
    if word == word.capitalize() and not is_camel_case_string(fixword):
        # word is capitalized and fixword(s) contain mixed with no camelCase.
        # Capitalize/Title fixword(s).
        # Eg. skipt->skip, Skype, skipped,
        return fixword.title()
    if word == word.upper():
        # word is in all upper case, change fixword to upper.
        # Eg. MONDAY
        return fixword.upper()
    if word.lower() == fixword.lower():
        # Special feature only meant for private custom dictionary.
        # word is valid but fixword required in CamelCase.
        # Use fixword as per dictionary.
        # Eg. mysql->MySQL
        return fixword
    # word is in lower, capitalize, CamelCase or whatever.
    # Use fixword as per dictionary.
    return fixword
