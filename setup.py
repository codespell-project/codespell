#! /usr/bin/env python

import contextlib
import os

from setuptools import setup

if __name__ == "__main__":
    with contextlib.suppress(FileNotFoundError):
        os.remove('MANIFEST')

    setup()
