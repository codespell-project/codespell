# -*- coding: utf-8 -*-

from __future__ import print_function

import contextlib
import os
import os.path as op
import subprocess
import sys
import tempfile
import warnings

from nose.tools import with_setup, assert_equal, assert_true

import codespell_lib as cs


def reload_codespell_lib():
    try:
        reload  # Python 2.7
    except NameError:
        try:
            from importlib import reload  # Python 3.4+
        except ImportError:
            from imp import reload  # Python 3.0 - 3.3
    reload(cs._codespell)


def run_codespell(args=(), cwd=None):
    """Helper to run codespell"""
    return subprocess.Popen(
        ['codespell'] + list(args), cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()


def test_command():
    """Test running the codespell executable"""
    # With no arguments does "."
    with TemporaryDirectory() as d:
        assert_equal(run_codespell(cwd=d), 0)
        with open(op.join(d, 'bad.txt'), 'w') as f:
            f.write('abandonned\nAbandonned\nABANDONNED\nAbAnDoNnEd')
        assert_equal(run_codespell(cwd=d), 4)


def test_basic():
    """Test some basic functionality"""
    assert_equal(cs.main('_does_not_exist_'), 0)
    with tempfile.NamedTemporaryFile('w') as f:
        pass
    with CaptureStdout() as sio:
        assert_equal(cs.main('-D', 'foo', f.name), 1)  # missing dictionary
    try:
        assert_true('cannot find dictionary' in sio[1])
        assert_equal(cs.main(f.name), 0)  # empty file
        with open(f.name, 'a') as f:
            f.write('this is a test file\n')
        assert_equal(cs.main(f.name), 0)  # good
        with open(f.name, 'a') as f:
            f.write('abandonned\n')
        assert_equal(cs.main(f.name), 1)  # bad
        with open(f.name, 'a') as f:
            f.write('abandonned\n')
        assert_equal(cs.main(f.name), 2)  # worse
    finally:
        os.remove(f.name)
    with TemporaryDirectory() as d:
        with open(op.join(d, 'bad.txt'), 'w') as f:
            f.write('abandonned\nAbandonned\nABANDONNED\nAbAnDoNnEd')
        assert_equal(cs.main(d), 4)
        with CaptureStdout() as sio:
            assert_equal(cs.main('-w', d), 0)
        assert_true('FIXED:' in sio[1])
        with open(op.join(d, 'bad.txt')) as f:
            new_content = f.read()
        assert_equal(cs.main(d), 0)
        assert_equal(new_content, 'abandoned\nAbandoned\nABANDONED\nabandoned')

        with open(op.join(d, 'bad.txt'), 'w') as f:
            f.write('abandonned abandonned\n')
        assert_equal(cs.main(d), 2)
        with CaptureStdout() as sio:
            assert_equal(cs.main('-q', '16', '-w', d), 0)
        assert_equal(sio[0], '')
        assert_equal(cs.main(d), 0)

        # empty directory
        os.mkdir(op.join(d, 'test'))
        assert_equal(cs.main(d), 0)

        # hidden file
        with open(op.join(d, 'test.txt'), 'w') as f:
            f.write('abandonned\n')
        assert_equal(cs.main(op.join(d, 'test.txt')), 1)
        os.rename(op.join(d, 'test.txt'), op.join(d, '.test.txt'))
        assert_equal(cs.main(op.join(d, '.test.txt')), 0)


def test_interactivity():
    """Test interaction"""
    # Windows can't read a currently-opened file, so here we use
    # NamedTemporaryFile just to get a good name
    with tempfile.NamedTemporaryFile('w') as f:
        pass
    try:
        assert_equal(cs.main(f.name), 0)  # empty file
        with open(f.name, 'w') as f:
            f.write('abandonned\n')
        assert_equal(cs.main('-i', '-1', f.name), 1)  # bad
        with FakeStdin('y\n'):
            assert_equal(cs.main('-i', '3', f.name), 1)
        with CaptureStdout() as sio:
            with FakeStdin('n\n'):
                assert_equal(cs.main('-w', '-i', '3', f.name), 0)
        assert_true('==>' in sio[0])
        with CaptureStdout():
            with FakeStdin('x\ny\n'):
                assert_equal(cs.main('-w', '-i', '3', f.name), 0)
        assert_equal(cs.main(f.name), 0)
    finally:
        os.remove(f.name)

    # New example
    with tempfile.NamedTemporaryFile('w') as f:
        pass
    try:
        with open(f.name, 'w') as f:
            f.write('abandonned\n')
        assert_equal(cs.main(f.name), 1)
        with CaptureStdout():
            with FakeStdin(' '):  # blank input -> Y
                assert_equal(cs.main('-w', '-i', '3', f.name), 0)
        assert_equal(cs.main(f.name), 0)
    finally:
        os.remove(f.name)

    # multiple options
    with tempfile.NamedTemporaryFile('w') as f:
        pass
    try:
        with open(f.name, 'w') as f:
            f.write('ackward\n')

        assert_equal(cs.main(f.name), 1)
        with CaptureStdout():
            with FakeStdin(' \n'):  # blank input -> nothing
                assert_equal(cs.main('-w', '-i', '3', f.name), 0)
        assert_equal(cs.main(f.name), 1)
        with CaptureStdout():
            with FakeStdin('0\n'):  # blank input -> nothing
                assert_equal(cs.main('-w', '-i', '3', f.name), 0)
        assert_equal(cs.main(f.name), 0)
        with open(f.name, 'r') as f_read:
            assert_equal(f_read.read(), 'awkward\n')
        with open(f.name, 'w') as f:
            f.write('ackward\n')
        assert_equal(cs.main(f.name), 1)
        with CaptureStdout() as sio:
            with FakeStdin('x\n1\n'):  # blank input -> nothing
                assert_equal(cs.main('-w', '-i', '3', f.name), 0)
        assert_true('a valid option' in sio[0])
        assert_equal(cs.main(f.name), 0)
        with open(f.name, 'r') as f:
            assert_equal(f.read(), 'backward\n')
    finally:
        os.remove(f.name)


def test_summary():
    """Test summary functionality"""
    with tempfile.NamedTemporaryFile('w') as f:
        pass
    try:
        with CaptureStdout() as sio:
            cs.main(f.name)
        for ii in range(2):
            assert_equal(sio[ii], '')  # no output
        with CaptureStdout() as sio:
            cs.main(f.name, '--summary')
        assert_equal(sio[1], '')  # stderr
        assert_true('SUMMARY' in sio[0])
        assert_equal(len(sio[0].split('\n')), 5)  # no output
        with open(f.name, 'w') as f:
            f.write('abandonned\nabandonned')
        with CaptureStdout() as sio:
            cs.main(f.name, '--summary')
        assert_equal(sio[1], '')  # stderr
        assert_true('SUMMARY' in sio[0])
        assert_equal(len(sio[0].split('\n')), 7)
        assert_true('abandonned' in sio[0].split()[-2])
    finally:
        os.remove(f.name)


@with_setup(reload_codespell_lib, reload_codespell_lib)
def test_ignore_dictionary():
    """Test ignore dictionary functionality"""
    with TemporaryDirectory() as d:
        with open(op.join(d, 'bad.txt'), 'w') as f:
            f.write('abandonned\nabondon\n')
        with tempfile.NamedTemporaryFile('w') as f:
            pass
        with open(f.name, 'w') as f:
            f.write('abandonned\n')
        assert_equal(cs.main('-I', f.name, d), 1)


@with_setup(reload_codespell_lib, reload_codespell_lib)
def test_custom_regex():
    """Test custom word regex"""
    with TemporaryDirectory() as d:
        with open(op.join(d, 'bad.txt'), 'w') as f:
            f.write('abandonned_abondon\n')
        assert_equal(cs.main(d), 0)
        assert_equal(cs.main('-r', "[a-z]+", d), 2)


def test_exclude_file():
    """Test exclude file functionality"""
    with TemporaryDirectory() as d:
        with open(op.join(d, 'bad.txt'), 'wb') as f:
            f.write('abandonned 1\nabandonned 2\n'.encode('utf-8'))
        assert_equal(cs.main(d), 2)
        with tempfile.NamedTemporaryFile('w') as f:
            pass
        with open(f.name, 'wb') as f:
            f.write('abandonned 1\n'.encode('utf-8'))
        assert_equal(cs.main(d), 2)
        assert_equal(cs.main('-x', f.name, d), 1)


def test_encoding():
    """Test encoding handling"""
    # Some simple Unicode things
    with tempfile.NamedTemporaryFile('wb') as f:
        pass
    # with CaptureStdout() as sio:
    assert_equal(cs.main(f.name), 0)
    try:
        with open(f.name, 'wb') as f:
            f.write(u'naïve\n'.encode('utf-8'))
        assert_equal(cs.main(f.name), 0)
        assert_equal(cs.main('-e', f.name), 0)
        with open(f.name, 'ab') as f:
            f.write(u'naieve\n'.encode('utf-8'))
        assert_equal(cs.main(f.name), 1)
        # Binary file warning
        with open(f.name, 'wb') as f:
            f.write(b'\x00\x00naiive\x00\x00')
        with CaptureStdout() as sio:
            assert_equal(cs.main(f.name), 0)
        assert_true('WARNING: Binary file' in sio[1])
        with CaptureStdout() as sio:
            assert_equal(cs.main('-q', '2', f.name), 0)
        assert_equal(sio[1], '')
    finally:
        os.remove(f.name)


def test_ignore():
    """Test ignoring of files and directories"""
    with TemporaryDirectory() as d:
        with open(op.join(d, 'good.txt'), 'w') as f:
            f.write('this file is okay')
        assert_equal(cs.main(d), 0)
        with open(op.join(d, 'bad.txt'), 'w') as f:
            f.write('abandonned')
        assert_equal(cs.main(d), 1)
        assert_equal(cs.main('--skip=bad*', d), 0)
        assert_equal(cs.main('--skip=bad.txt', d), 0)
        subdir = op.join(d, 'ignoredir')
        os.mkdir(subdir)
        with open(op.join(subdir, 'bad.txt'), 'w') as f:
            f.write('abandonned')
        assert_equal(cs.main(d), 2)
        assert_equal(cs.main('--skip=bad*', d), 0)
        assert_equal(cs.main('--skip=*ignoredir*', d), 1)
        assert_equal(cs.main('--skip=ignoredir', d), 1)


def test_check_filename():
    """Test filename check"""
    with TemporaryDirectory() as d:
        with open(op.join(d, 'abandonned.txt'), 'w') as f:
            f.write('.')
        assert_equal(cs.main('-f', d), 1)


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
