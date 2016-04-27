from __future__ import print_function

import os
import os.path as op
import sys
import tempfile
import warnings

from nose.tools import assert_equal

from codespell_lib import main


def test_basic():
    """Test some basic functionality"""
    assert_equal(main('_does_not_exist_'), 0)
    with tempfile.NamedTemporaryFile() as f:
        assert_equal(main(f.name,), 0)  # empty file
        f.write('this is a test file\n'.encode('utf-8'))
        f.flush()
        assert_equal(main(f.name,), 0)  # good
        f.write('abandonned\n'.encode('utf-8'))
        f.flush()
        assert_equal(main(f.name), 1)  # bad
        f.write('abandonned\n'.encode('utf-8'))
        f.flush()
        assert_equal(main(f.name), 2)  # worse


def test_ignore():
    """Test ignoring of files and directories"""
    with TemporaryDirectory() as d:
        with open(op.join(d, 'good.txt'), 'w') as f:
            f.write('this file is okay')
        assert_equal(main(d), 0)
        with open(op.join(d, 'bad.txt'), 'w') as f:
            f.write('abandonned')
        assert_equal(main(d), 1)
        assert_equal(main('--skip=bad*', d), 0)
        assert_equal(main('--skip=bad.txt', d), 0)
        subdir = op.join(d, 'ignoredir')
        os.mkdir(subdir)
        with open(op.join(subdir, 'bad.txt'), 'w') as f:
            f.write('abandonned')
        assert_equal(main(d), 2)
        assert_equal(main('--skip=bad*', d), 0)
        assert_equal(main('--skip=*ignoredir*', d), 1)


class TemporaryDirectory(object):
    """Backport for 2.7"""

    def __init__(self, suffix="", prefix="tmp", dir=None):
        self._closed = False
        self.name = None
        self.name = tempfile.mkdtemp(suffix, prefix, dir)

    def __enter__(self):
        return self.name

    def cleanup(self, _warn=False):
        if self.name and not self._closed:
            try:
                self._rmtree(self.name)
            except (TypeError, AttributeError) as ex:
                # Issue #10188: Emit a warning on stderr
                # if the directory could not be cleaned
                # up due to missing globals
                if "None" not in str(ex):
                    raise
                print("ERROR: {!r} while cleaning up {!r}".format(ex, self,),
                      file=sys.stderr)
                return
            self._closed = True
            if _warn:
                self._warn("Implicitly cleaning up {!r}".format(self))

    def __exit__(self, exc, value, tb):
        self.cleanup()

    def __del__(self):
        # Issue a ResourceWarning if implicit cleanup needed
        self.cleanup(_warn=True)

    # XXX (ncoghlan): The following code attempts to make
    # this class tolerant of the module nulling out process
    # that happens during CPython interpreter shutdown
    # Alas, it doesn't actually manage it. See issue #10188
    _listdir = staticmethod(os.listdir)
    _path_join = staticmethod(os.path.join)
    _isdir = staticmethod(os.path.isdir)
    _islink = staticmethod(os.path.islink)
    _remove = staticmethod(os.remove)
    _rmdir = staticmethod(os.rmdir)
    _warn = warnings.warn

    def _rmtree(self, path):
        # Essentially a stripped down version of shutil.rmtree.  We can't
        # use globals because they may be None'ed out at shutdown.
        for name in self._listdir(path):
            fullname = self._path_join(path, name)
            try:
                isdir = self._isdir(fullname) and not self._islink(fullname)
            except OSError:
                isdir = False
            if isdir:
                self._rmtree(fullname)
            else:
                try:
                    self._remove(fullname)
                except OSError:
                    pass
        try:
            self._rmdir(path)
        except OSError:
            pass
