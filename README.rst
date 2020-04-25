codespell
=========

Fix common misspellings in text files. It's designed primarily for checking
misspelled words in source code, but it can be used with other files as well.

Useful links
------------

* `GitHub project <https://github.com/codespell-project/codespell>`_

* Mailing list: <codespell@googlegroups.com> with web archives/interface
  `here <https://groups.google.com/forum/?fromgroups#!forum/codespell>`_

* `Repository <https://github.com/codespell-project/codespell>`_

* `Releases <https://github.com/codespell-project/codespell/releases>`_

Requirements
------------

Python 2.7 or above.

Installation
------------

You can use ``pip`` to install codespell with e.g.::

    pip install codespell

Usage
-----

For more in depth info please check usage with ``codespell -h``.

Some noteworthy flags::

    codespell -w, --write-changes

The ``-w`` flag will actually implement the changes recommended by codespell. Not running with ``-w`` flag is the same as with doing a dry run. It is recommended to run this with the ``-i`` or ``--interactive`` flag.::

    codespell -I FILE, --ignore-words=FILE

The ``-I`` flag can be used to whitelist certain words that are in the ``codespell_lib/data/dictionary.txt``. The format of the whitelist file is one word per line. Invoke using: ``codespell -I path/to/file.txt`` to execute codespell referencing said whitelist. **Important note:** The whitelist passed to ``-I`` is case-sensitive based on how it is listed in ``dictionary.txt``. ::

    codespell -L word1,word2,word3,word4

The ``-L`` flag can be used to whitelist certain words that are comma-separated placed immediately after it. ::

    codespell -S, --skip=

Comma-separated list of files to skip. It accepts globs as well.  Examples:

* to skip .eps & .txt files, invoke ``codespell --skip="*.eps,*.txt"``

* to skip directories, invoke ``codespell --skip="./src/3rd-Party,./src/Test"``


Useful commands::

    codespell -d -q 3 --skip="*.po,*.ts,./src/3rdParty,./src/Test"

List all typos found except translation files and some directories.
Display them without terminal colors and with a quiet level of 3. ::

    codespell -i 3 -w

Run interactive mode level 3 and write changes to file.

We ship a dictionary that is an improved version of the one available
`on Wikipedia <https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines>`_
after applying them in projects like Linux Kernel, EFL, oFono among others.
You can provide your own version of the dictionary, but patches for
new/different entries are very welcome.

Want to know if a word you're proposing exists in codespell already? It is possible to test a word against the current dictionary that exists in ``codespell_lib/data/dictionary.txt`` via::

    echo "word" | codespell -
    echo "1stword,2ndword" | codespell -

Dictionary format
-----------------

The format of the dictionary was influenced by the one it originally came from,
i.e. from Wikipedia. The difference is how multiple options are treated and
that the last argument is the reason why a certain entry could not be applied
directly, but instead be manually inspected. E.g.:

1. Simple entry: one wrong word / one suggestion::

        calulated->calculated

2. Entry with more than one suggested fix::

       fiel->feel, field, file, phial,

   Note the last comma! You need to use it, otherwise the last suggestion
   will be discarded (see below for why). When there is more than one
   suggestion, an automatic fix is not possible and the best we can do is
   to give the user the file and line where the error occurred as well as
   the suggestions.

3. Entry with one word, but with automatically fix disabled::

       clas->class, disabled because of name clash in c++

   Note that there isn't a comma in the end of the line. The last argument is
   treated as the reason why a suggestion cannot be automatically applied.

Sending Pull Requests
---------------------

If you have a suggested typo that you'd like to see merged please follow these steps:

1. Make sure you read the instructions mentioned in the ``Dictionary format`` section above to submit correctly formatted entries.

2. Sort the dictionary. This is done by invoking (in the top level directory of ``codespell/``)::

       make check-dictionaries

   If the make script finds that you need to sort the dictionary, please then run::

       make sort-dictionaries

3. Only after this process is complete do we recommend you submit the PR.

**Important Notes:**

* If the dictionary is submitted without being pre-sorted the PR will fail via TravisCI.
* Not all PRs will be merged. This is pending on the discretion of the devs, maintainers, and the community.

Updating
--------

To stay current with codespell developments it is possible to build codespell from GitHub via::

    pip install --upgrade git+https://github.com/codespell-project/codespell.git

**Important Notes:**

* Sometimes installing via ``pip`` will complain about permissions. If this is the case then run with ::

    pip install --user --upgrade git+https://github.com/codespell-project/codespell.git

* It has been reported that after installing from ``pip``, codespell can't be located. Please check the $PATH variable to see if ``~/.local/bin`` is present. If it isn't then add it to your path.
* If you decide to install via ``pip`` then be sure to remove any previously installed versions of codespell (via your platform's preferred app manager).

Updating the dictionary
-----------------------

In the scenario where the user prefers not to follow the development version of codespell yet still opts to benefit from the frequently updated `dictionary.txt` file, we recommend running a simple set of commands to achieve this ::

    wget https://raw.githubusercontent.com/codespell-project/codespell/master/codespell_lib/data/dictionary.txt
    codespell -D dictionary.txt

The above simply downloads the latest ``dictionary.txt`` file and then by utilizing the ``-D`` flag allows the user to specify the freshly downloaded ``dictionary.txt`` as the custom dictionary instead of the default one.

License
-------

The Python script ``codespell`` with its library ``codespell_lib`` is available
with the following terms:
(*tl;dr*: `GPL v2`_)

   Copyright (C) 2010-2011  Lucas De Marchi <lucas.de.marchi@gmail.com>

   Copyright (C) 2011  ProFUSION embedded systems

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; version 2 of the License.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, see
   <http://www.gnu.org/licenses/old-licenses/gpl-2.0.html>.

.. _GPL v2: http://www.gnu.org/licenses/old-licenses/gpl-2.0.html

dictionary.txt is a derived work of English Wikipedia and is released under the
Creative Commons Attribution-Share-Alike License 3.0
http://creativecommons.org/licenses/by-sa/3.0/
