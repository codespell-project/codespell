#! /usr/bin/env python

# adapted from mne-python

import os
from os import path as op

from setuptools import setup

from codespell_lib import __version__

DISTNAME = 'codespell'
DESCRIPTION = """Codespell"""
MAINTAINER = 'Lucas De Marchi'
MAINTAINER_EMAIL = 'lucas.de.marchi@gmail.com'
URL = 'https://github.com/codespell-project/codespell/'
LICENSE = 'GPL v2'
DOWNLOAD_URL = 'https://github.com/codespell-project/codespell/'
with open('README.rst', 'r') as f:
    LONG_DESCRIPTION = f.read()

if __name__ == "__main__":
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    setup(name=DISTNAME,
          maintainer=MAINTAINER,
          include_package_data=True,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          license=LICENSE,
          url=URL,
          version=__version__,
          download_url=DOWNLOAD_URL,
          long_description=LONG_DESCRIPTION,
          zip_safe=False,
          classifiers=['Intended Audience :: Developers',
                       'License :: OSI Approved',
                       'Programming Language :: Python',
                       'Topic :: Software Development',
                       'Operating System :: Microsoft :: Windows',
                       'Operating System :: POSIX',
                       'Operating System :: Unix',
                       'Operating System :: MacOS'],
          platforms='any',
          packages=[
              'codespell_lib', 'codespell_lib.tests',
              'codespell_lib.data',
          ],
          package_data={'codespell_lib': [
              op.join('data', 'dictionary.txt'),
              op.join('data', 'linux-kernel.exclude'),
          ]},
          entry_points={
              'console_scripts': [
                  'codespell = codespell_lib:_script_main'
              ],
          }
          )
