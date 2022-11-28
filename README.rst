codespell
=========

Fix common misspellings in text files. It's designed primarily for checking
misspelled words in source code, but it can be used with other files as well.
It does not check for word membership in a complete dictionary, but instead
looks for a set of common misspellings. Therefore it should catch errors like
"adn", but it will not catch "adnasdfasdf". This also means it shouldn't
generate false-positives when you use a niche term it doesn't know about.

Useful links
------------

* `GitHub project <https://github.com/codespell-project/codespell>`_

* `Repository <https://github.com/codespell-project/codespell>`_

* `Releases <https://github.com/codespell-project/codespell/releases>`_

Requirements
------------

Python 3.7 or above.

Installation
------------

You can use ``pip`` to install codespell with e.g.:

.. code-block:: sh

    pip install codespell

Usage
-----

For more in depth info please check usage with ``codespell -h``.

Some noteworthy flags:

.. code-block:: sh

    codespell -w, --write-changes

The ``-w`` flag will actually implement the changes recommended by codespell. Not running with ``-w`` flag is the same as with doing a dry run. It is recommended to run this with the ``-i`` or ``--interactive`` flag.

.. code-block:: sh

    codespell -I FILE, --ignore-words=FILE

The ``-I`` flag can be used for a list of certain words to allow that are in the codespell dictionaries. The format of the file is one word per line. Invoke using: ``codespell -I path/to/file.txt`` to execute codespell referencing said list of allowed words. **Important note:** The list passed to ``-I`` is case-sensitive based on how it is listed in the codespell dictionaries.

.. code-block:: sh

    codespell -L word1,word2,word3,word4

The ``-L`` flag can be used to allow certain words that are comma-separated placed immediately after it.  **Important note:** The list passed to ``-L`` is case-sensitive based on how it is listed in the codespell dictionaries.

.. code-block:: sh

    codespell -x FILE, --exclude-file=FILE

Ignore whole lines that match those in ``FILE``.  The lines in ``FILE`` should match the to-be-excluded lines exactly.

.. code-block:: sh

    codespell -S, --skip=

Comma-separated list of files to skip. It accepts globs as well.  Examples:

* to skip .eps & .txt files, invoke ``codespell --skip="*.eps,*.txt"``

* to skip directories, invoke ``codespell --skip="./src/3rd-Party,./src/Test"``


Useful commands:

.. code-block:: sh

    codespell -d -q 3 --skip="*.po,*.ts,./src/3rdParty,./src/Test"

List all typos found except translation files and some directories.
Display them without terminal colors and with a quiet level of 3.

.. code-block:: sh

    codespell -i 3 -w

Run interactive mode level 3 and write changes to file.

We ship a collection of dictionaries that are an improved version of the one available
`on Wikipedia <https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines>`_
after applying them in projects like Linux Kernel, EFL, oFono among others.
You can provide your own version of the dictionary, but patches for
new/different entries are very welcome.

Want to know if a word you're proposing exists in codespell already? It is possible to test a word against the current set dictionaries that exist in ``codespell_lib/data/dictionary*.txt`` via:

.. code-block:: sh

    echo "word" | codespell -
    echo "1stword,2ndword" | codespell -

You can select the optional dictionaries with the ``--builtin`` option.

Using a config file
-------------------

Command line options can also be specified in a config file.

When running ``codespell``, it will check in the current directory for a file
named ``setup.cfg`` or ``.codespellrc`` (or a file specified via ``--config``),
containing an entry named ``[codespell]``. Each command line argument can
be specified in this file (without the preceding dashes), for example:

.. code-block:: ini

    [codespell]
    skip = *.po,*.ts,./src/3rdParty,./src/Test
    count =
    quiet-level = 3

Codespell will also check in the current directory for a ``pyproject.toml``
(or a path can be specified via ``--toml <filename>``) file, and the
``[tool.codespell]`` entry will be used as long as the tomli_ package
is installed, for example:

.. code-block:: toml

    [tool.codespell]
    skip = '*.po,*.ts,./src/3rdParty,./src/Test'
    count = ''
    quiet-level = 3

These are both equivalent to running:

.. code-block:: sh

    codespell --quiet-level 3 --count --skip "*.po,*.ts,./src/3rdParty,./src/Test"

If several config files are present, they are read in the following order:

#. ``pyproject.toml`` (only if the ``tomli`` library is available)
#. ``setup.cfg``
#. ``.codespellrc``
#. any additional file supplied via ``--config``

If a codespell configuration is supplied in several of these files,
the configuration from the most recently read file overwrites previously
specified configurations.

Any options specified in the command line will *override* options from the
config files.

.. _tomli: https://pypi.org/project/tomli/

Dictionary format
-----------------

The format of the dictionaries was influenced by the one they originally came from,
i.e. from Wikipedia. The difference is how multiple options are treated and
that the last argument is an optional reason why a certain entry could not be
applied directly, but should instead be manually inspected. E.g.:

1. Simple entry: one wrong word / one suggestion::

        calulated->calculated

2. Entry with more than one suggested fix::

       fiel->feel, field, file, phial,

   Note the last comma! You need to use it, otherwise the last suggestion
   will be discarded (see below for why). When there is more than one
   suggestion, an automatic fix is not possible and the best we can do is
   to give the user the file and line where the error occurred as well as
   the suggestions.

3. Entry with one word, but with automatic fix disabled::

       clas->class, disabled because of name clash in c++

   Note that there isn't a comma at the end of the line. The last argument is
   treated as the reason why a suggestion cannot be automatically applied.

   There can also be multiple suggestions but any automatic fix will again be
   disabled::

       clas->class, clash, disabled because of name clash in c++

Development Setup
-----------------

As suggested in the `Python Packaging User Guide`_, ensure ``pip``, ``setuptools``, and ``wheel`` are up to date before installing from source. Specifically you will need recent versions of ``setuptools`` and ``setuptools_scm``:

.. code-block:: sh

    pip install --upgrade pip setuptools setuptools_scm wheel

You can install required dependencies for development by running the following within a checkout of the codespell source:

.. code-block:: sh

       pip install -e ".[dev]"

To run tests against the codebase run:

.. code-block:: sh

       make check

.. _Python Packaging User Guide: https://packaging.python.org/en/latest/tutorials/installing-packages/#requirements-for-installing-packages

Sending Pull Requests
---------------------

If you have a suggested typo that you'd like to see merged please follow these steps:

1. Make sure you read the instructions mentioned in the ``Dictionary format`` section above to submit correctly formatted entries.

2. Choose the correct dictionary file to add your typo to. See `codespell --help` for explanations of the different dictionaries.

3. Sort the dictionaries. This is done by invoking (in the top level directory of ``codespell/``):

   .. code-block:: sh

       make check-dictionaries

   If the make script finds that you need to sort a dictionary, please then run:

   .. code-block:: sh

       make sort-dictionaries

4. Only after this process is complete do we recommend you submit the PR.

**Important Notes:**

* If the dictionaries are submitted without being pre-sorted the PR will fail via our various CI tools.
* Not all PRs will be merged. This is pending on the discretion of the devs, maintainers, and the community.

Updating
--------

To stay current with codespell developments it is possible to build codespell from GitHub via:

.. code-block:: sh

    pip install --upgrade git+https://github.com/codespell-project/codespell.git

**Important Notes:**

* Sometimes installing via ``pip`` will complain about permissions. If this is the case then run with:

  .. code-block:: sh

      pip install --user --upgrade git+https://github.com/codespell-project/codespell.git

* It has been reported that after installing from ``pip``, codespell can't be located. Please check the $PATH variable to see if ``~/.local/bin`` is present. If it isn't then add it to your path.
* If you decide to install via ``pip`` then be sure to remove any previously installed versions of codespell (via your platform's preferred app manager).

Updating the dictionaries
-------------------------

In the scenario where the user prefers not to follow the development version of codespell yet still opts to benefit from the frequently updated dictionary files, we recommend running a simple set of commands to achieve this:

.. code-block:: sh

    wget https://raw.githubusercontent.com/codespell-project/codespell/master/codespell_lib/data/dictionary.txt
    codespell -D dictionary.txt

The above simply downloads the latest ``dictionary.txt`` file and then by utilizing the ``-D`` flag allows the user to specify the freshly downloaded ``dictionary.txt`` as the custom dictionary instead of the default one.

You can also do the same thing for the other dictionaries listed here:
    https://github.com/codespell-project/codespell/tree/master/codespell_lib/data

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

``dictionary.txt`` and the other ``dictionary_*.txt`` files are derivative works of English Wikipedia and are released under the `Creative Commons Attribution-Share-Alike License 3.0 <http://creativecommons.org/licenses/by-sa/3.0/>`_.
