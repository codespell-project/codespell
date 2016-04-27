# -*- coding: utf-8 -*-

from __future__ import print_function

import contextlib
import os
import os.path as op
import sys
import tempfile
import warnings

from nose.tools import assert_equal, assert_true

from codespell_lib import main


def test_basic():
    """Test some basic functionality"""
    assert_equal(main('_does_not_exist_'), 0)
    with tempfile.NamedTemporaryFile('w') as f:
        with CaptureStdout() as sio:
            assert_equal(main('-D', 'foo', f.name), 1)  # missing dictionary
        assert_true('cannot find dictionary' in sio[1])
        assert_equal(main(f.name), 0)  # empty file
        f.write('this is a test file\n')
        f.flush()
        assert_equal(main(f.name), 0)  # good
        f.write('abandonned\n')
        f.flush()
        assert_equal(main(f.name), 1)  # bad
        f.write('abandonned\n')
        f.flush()
        assert_equal(main(f.name), 2)  # worse
    with TemporaryDirectory() as d:
        with open(op.join(d, 'bad.txt'), 'w') as f:
            f.write('abandonned\nAbandonned\nABANDONNED\nAbAnDoNnEd')
        assert_equal(main(d), 4)
        with CaptureStdout() as sio:
            assert_equal(main('-w', d), 0)
        assert_true('FIXED:' in sio[1])
        with open(op.join(d, 'bad.txt')) as f:
            new_content = f.read()
        assert_equal(main(d), 0)
        assert_equal(new_content, 'abandoned\nAbandoned\nABANDONED\nabandoned')

        with open(op.join(d, 'bad.txt'), 'w') as f:
            f.write('abandonned abandonned\n')
        assert_equal(main(d), 2)
        with CaptureStdout() as sio:
            assert_equal(main('-q', '16', '-w', d), 0)
        assert_equal(sio[0], '')
        assert_equal(main(d), 0)

        # empty directory
        os.mkdir(op.join(d, 'test'))
        assert_equal(main(d), 0)

        # hidden file
        with open(op.join(d, 'test.txt'), 'w') as f:
            f.write('abandonned\n')
        assert_equal(main(op.join(d, 'test.txt')), 1)
        os.rename(op.join(d, 'test.txt'), op.join(d, '.test.txt'))
        assert_equal(main(op.join(d, '.test.txt')), 0)


def test_interactivity():
    """Test interaction"""
    with tempfile.NamedTemporaryFile('w') as f:
        assert_equal(main(f.name), 0)  # empty file
        f.write('abandonned\n')
        f.flush()
        assert_equal(main('-i', '-1', f.name), 1)  # bad
        with FakeStdin('y\n'):
            assert_equal(main('-i', '3', f.name), 1)
        with CaptureStdout() as sio:
            with FakeStdin('n\n'):
                assert_equal(main('-w', '-i', '3', f.name), 0)
        assert_true('==>' in sio[0])
        with CaptureStdout():
            with FakeStdin('x\ny\n'):
                assert_equal(main('-w', '-i', '3', f.name), 0)
        assert_equal(main(f.name), 0)
    with tempfile.NamedTemporaryFile('w') as f:
        f.write('abandonned\n')
        f.flush()
        assert_equal(main(f.name), 1)
        with CaptureStdout():
            with FakeStdin(' '):  # blank input -> Y
                assert_equal(main('-w', '-i', '3', f.name), 0)
        assert_equal(main(f.name), 0)
    # multiple options
    with tempfile.NamedTemporaryFile('w') as f:
        f.write('ackward\n')
        f.flush()
        assert_equal(main(f.name), 1)
        with CaptureStdout():
            with FakeStdin(' \n'):  # blank input -> nothing
                assert_equal(main('-w', '-i', '3', f.name), 0)
        assert_equal(main(f.name), 1)
        with CaptureStdout():
            with FakeStdin('0\n'):  # blank input -> nothing
                assert_equal(main('-w', '-i', '3', f.name), 0)
        assert_equal(main(f.name), 0)
        with open(f.name, 'r') as f_read:
            assert_equal(f_read.read(), 'awkward\n')
        f.seek(0)
        f.write('ackward\n')
        f.flush()
        assert_equal(main(f.name), 1)
        with CaptureStdout() as sio:
            with FakeStdin('x\n1\n'):  # blank input -> nothing
                assert_equal(main('-w', '-i', '3', f.name), 0)
        assert_true('a valid option' in sio[0])
        assert_equal(main(f.name), 0)
        with open(f.name, 'r') as f:
            assert_equal(f.read(), 'backward\n')


def test_summary():
    """Test summary functionality"""
    with tempfile.NamedTemporaryFile('w') as f:
        with CaptureStdout() as sio:
            main(f.name)
        for ii in range(2):
            assert_equal(sio[ii], '')  # no output
        with CaptureStdout() as sio:
            main(f.name, '--summary')
        assert_equal(sio[1], '')  # stderr
        assert_true('SUMMARY' in sio[0])
        assert_equal(len(sio[0].split('\n')), 5)  # no output
        f.write('abandonned\nabandonned')
        f.flush()
        with CaptureStdout() as sio:
            main(f.name, '--summary')
        assert_equal(sio[1], '')  # stderr
        assert_true('SUMMARY' in sio[0])
        assert_equal(len(sio[0].split('\n')), 7)
        assert_true('abandonned' in sio[0].split()[-2])


def test_exclude_file():
    """Test exclude file functionality"""
    with TemporaryDirectory() as d:
        with open(op.join(d, 'bad.txt'), 'w') as f:
            f.write('abandonned 1\nabandonned 2\n')
        with tempfile.NamedTemporaryFile('w') as f:
            f.write('abandonned 1\n')
            f.flush()
            assert_equal(main(d), 2)
            assert_equal(main('-x', f.name, d), 1)


def test_encoding():
    """Test encoding handling"""
    # Some simple Unicode things
    with tempfile.NamedTemporaryFile('wb') as f:
        # with CaptureStdout() as sio:
        assert_equal(main(f.name), 0)
        f.write(u'naïve\n'.encode('utf-8'))
        f.flush()
        assert_equal(main(f.name), 0)
        assert_equal(main('-e', f.name), 0)
        f.write(u'naieve\n'.encode('utf-8'))
        f.flush()
        assert_equal(main(f.name), 1)
    # Binary file warning
    with tempfile.NamedTemporaryFile('wb') as f:
        assert_equal(main(f.name), 0)
        f.write(b'\x00\x00naiive\x00\x00')
        f.flush()
        with CaptureStdout() as sio:
            assert_equal(main(f.name), 0)
        assert_true('WARNING: Binary file' in sio[1])
        with CaptureStdout() as sio:
            assert_equal(main('-q', '2', f.name), 0)
        assert_equal(sio[1], '')


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


@contextlib.contextmanager
def CaptureStdout():
    if sys.version[0] == '2':
        from StringIO import StringIO
    else:
        from io import StringIO
    oldout, olderr = sys.stdout, sys.stderr
    try:
        out = [StringIO(), StringIO()]
        sys.stdout, sys.stderr = out
        yield out
    finally:
        sys.stdout, sys.stderr = oldout, olderr
        out[0] = out[0].getvalue()
        out[1] = out[1].getvalue()


@contextlib.contextmanager
def FakeStdin(text):
    if sys.version[0] == '2':
        from StringIO import StringIO
    else:
        from io import StringIO
    oldin = sys.stdin
    try:
        in_ = StringIO(text)
        sys.stdin = in_
        yield
    finally:
        sys.stdin = oldin
