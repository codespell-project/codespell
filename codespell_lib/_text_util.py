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

from typing import Sequence


def fix_case(word: str, candidates: Sequence[str]) -> Sequence[str]:
    if word == word.capitalize():
        return tuple(c.capitalize() for c in candidates)
    if word == word.upper():
        return tuple(c.upper() for c in candidates)
    # they are both lower case
    # or we don't have any idea
    return candidates
