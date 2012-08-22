codespell
=========

Fix common misspellings in text files. It's designed primarily for checking
misspelled words in source code, but it can be used with other files as well.

Information
-----------

GitHub project: <https://github.com/lucasdemarchi/codespell>

Mailing list: <codespell@googlegroups.com> with web archives/interface at
 <https://groups.google.com/forum/?fromgroups#!forum/codespell>

Usage
-----

Check usage with `./codespell -h`. There are a few command line options. We ship
a dictionary that is an improved version of the one available at
<http://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines>
after applying them in projects like Linux Kernel, EFL, oFono among others.
You can provide your own version of the directory, but patches for
new/different entries are very welcome.

Dictionary format
-----------------

The format of the dictionary was influenced by the one it originally came from,
i.e. from wikipedia. The difference is how multiple options are treated and
that the last argument is the reason why a certain entry could not be applied
directly, but instead be manually inspected. E.g:

1. Simple entry: one wrong word / one suggestion

    `calulated->calculated`

2. Entry with more than one suggested fix

    `fiel->feel, field, file, phial,`

    Note the last comma! You need to use it, otherwise the last suggestion
will be discarded (see below for why). When there are more than one
suggestion, automatically fix is not possible and the best we can do is
to give the user the file and line where the error occurred as well as
the suggestions.

3. Entry with one word, but with automatically fix disabled

    `clas->class, disabled because of name clash in c++`

   Note that there isn't a comma in the end of the line. The last argument is
treated as the reason why a suggestion can not be automatically applied.

License
-------

The Python script `codespell.py` is available with the following terms:
(*tl;dr*: [GPL v2][])

> Copyright (C) 2010-2011  Lucas De Marchi <lucas.de.marchi@gmail.com>

> Copyright (C) 2011  ProFUSION embedded systems

> This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

> This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

> You should have received a copy of the GNU General Public License
along with this program; if not, see
<http://www.gnu.org/licenses/old-licenses/gpl-2.0.html>.

[GPL v2]:http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
