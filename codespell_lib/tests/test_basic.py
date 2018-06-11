# -*- coding: utf-8 -*-

from __future__ import print_function

import contextlib
import os
import os.path as op
import subprocess
import sys
import tempfile
import warnings

import pytest

import codespell_lib as cs


@pytest.fixture(scope='function')
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
        assert run_codespell(cwd=d) == 0
        with open(op.join(d, 'bad.txt'), 'w') as f:
            f.write('abandonned\nAbandonned\nABANDONNED\nAbAnDoNnEd')
        assert run_codespell(cwd=d) == 4


def test_basic():
    """Test some basic functionality"""
    assert cs.main('_does_not_exist_') == 0
    with tempfile.NamedTemporaryFile('w') as f:
        pass
    with CaptureStdout() as sio:
        assert cs.main('-D', 'foo', f.name) == 1, 'missing dictionary'
    try:
        assert 'cannot find dictionary' in sio[1]
        assert cs.main(f.name) == 0, 'empty file'
        with open(f.name, 'a') as f:
            f.write('this is a test file\n')
        assert cs.main(f.name) == 0, 'good'
        with open(f.name, 'a') as f:
            f.write('abandonned\n')
        assert cs.main(f.name) == 1, 'bad'
        with open(f.name, 'a') as f:
            f.write('abandonned\n')
        assert cs.main(f.name) == 2, 'worse'
    finally:
        os.remove(f.name)
    with TemporaryDirectory() as d:
        with open(op.join(d, 'bad.txt'), 'w') as f:
            f.write('abandonned\nAbandonned\nABANDONNED\nAbAnDoNnEd')
        assert cs.main(d) == 4
        with CaptureStdout() as sio:
            assert cs.main('-w', d) == 0
        assert 'FIXED:' in sio[1]
        with open(op.join(d, 'bad.txt')) as f:
            new_content = f.read()
        assert cs.main(d) == 0
        assert new_content == 'abandoned\nAbandoned\nABANDONED\nabandoned'

        with open(op.join(d, 'bad.txt'), 'w') as f:
            f.write('abandonned abandonned\n')
        assert cs.main(d) == 2
        with CaptureStdout() as sio:
            assert cs.main('-q', '16', '-w', d) == 0
        assert sio[0] == ''
        assert cs.main(d) == 0

        # empty directory
        os.mkdir(op.join(d, 'test'))
        assert cs.main(d) == 0

        # hidden file
        with open(op.join(d, 'test.txt'), 'w') as f:
            f.write('abandonned\n')
        assert cs.main(op.join(d, 'test.txt')) == 1
        os.rename(op.join(d, 'test.txt'), op.join(d, '.test.txt'))
        assert cs.main(op.join(d, '.test.txt')) == 0


def test_interactivity():
    """Test interaction"""
    # Windows can't read a currently-opened file, so here we use
    # NamedTemporaryFile just to get a good name
    with tempfile.NamedTemporaryFile('w') as f:
        pass
    try:
        assert cs.main(f.name) == 0, 'empty file'
        with open(f.name, 'w') as f:
            f.write('abandonned\n')
        assert cs.main('-i', '-1', f.name) == 1, 'bad'
        with FakeStdin('y\n'):
            assert cs.main('-i', '3', f.name) == 1
        with CaptureStdout() as sio:
            with FakeStdin('n\n'):
                assert cs.main('-w', '-i', '3', f.name) == 0
        assert '==>' in sio[0]
        with CaptureStdout():
            with FakeStdin('x\ny\n'):
                assert cs.main('-w', '-i', '3', f.name) == 0
        assert cs.main(f.name) == 0
    finally:
        os.remove(f.name)

    # New example
    with tempfile.NamedTemporaryFile('w') as f:
        pass
    try:
        with open(f.name, 'w') as f:
            f.write('abandonned\n')
        assert cs.main(f.name) == 1
        with CaptureStdout():
            with FakeStdin(' '):  # blank input -> Y
                assert cs.main('-w', '-i', '3', f.name) == 0
        assert cs.main(f.name) == 0
    finally:
        os.remove(f.name)

    # multiple options
    with tempfile.NamedTemporaryFile('w') as f:
        pass
    try:
        with open(f.name, 'w') as f:
            f.write('ackward\n')

        assert cs.main(f.name) == 1
        with CaptureStdout():
            with FakeStdin(' \n'):  # blank input -> nothing
                assert cs.main('-w', '-i', '3', f.name) == 0
        assert cs.main(f.name) == 1
        with CaptureStdout():
            with FakeStdin('0\n'):  # blank input -> nothing
                assert cs.main('-w', '-i', '3', f.name) == 0
        assert cs.main(f.name) == 0
        with open(f.name, 'r') as f_read:
            assert f_read.read() == 'awkward\n'
        with open(f.name, 'w') as f:
            f.write('ackward\n')
        assert cs.main(f.name) == 1
        with CaptureStdout() as sio:
            with FakeStdin('x\n1\n'):  # blank input -> nothing
                assert cs.main('-w', '-i', '3', f.name) == 0
        assert 'a valid option' in sio[0]
        assert cs.main(f.name) == 0
        with open(f.name, 'r') as f:
            assert f.read() == 'backward\n'
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
            assert sio[ii] == '', 'no output'
        with CaptureStdout() as sio:
            cs.main(f.name, '--summary')
        assert sio[1] == '', 'stderr'
        assert 'SUMMARY' in sio[0]
        assert len(sio[0].split('\n')) == 5, 'no output'
        with open(f.name, 'w') as f:
            f.write('abandonned\nabandonned')
        with CaptureStdout() as sio:
            cs.main(f.name, '--summary')
        assert sio[1] == '', 'stderr'
        assert 'SUMMARY' in sio[0]
        assert len(sio[0].split('\n')) == 7
        assert 'abandonned' in sio[0].split()[-2]
    finally:
        os.remove(f.name)


def test_ignore_dictionary(reload_codespell_lib):
    """Test ignore dictionary functionality"""
    with TemporaryDirectory() as d:
        with open(op.join(d, 'bad.txt'), 'w') as f:
            f.write('abandonned\nabondon\n')
        with tempfile.NamedTemporaryFile('w') as f:
            pass
        with open(f.name, 'w') as f:
            f.write('abandonned\n')
        assert cs.main('-I', f.name, d) == 1


def test_custom_regex(reload_codespell_lib):
    """Test custom word regex"""
    with TemporaryDirectory() as d:
        with open(op.join(d, 'bad.txt'), 'w') as f:
            f.write('abandonned_abondon\n')
        assert cs.main(d) == 0
        assert cs.main('-r', "[a-z]+", d) == 2


def test_exclude_file():
    """Test exclude file functionality"""
    with TemporaryDirectory() as d:
        with open(op.join(d, 'bad.txt'), 'wb') as f:
            f.write('abandonned 1\nabandonned 2\n'.encode('utf-8'))
        assert cs.main(d) == 2
        with tempfile.NamedTemporaryFile('w') as f:
            pass
        with open(f.name, 'wb') as f:
            f.write('abandonned 1\n'.encode('utf-8'))
        assert cs.main(d) == 2
        assert cs.main('-x', f.name, d) == 1


def test_encoding():
    """Test encoding handling"""
    # Some simple Unicode things
    with tempfile.NamedTemporaryFile('wb') as f:
        pass
    # with CaptureStdout() as sio:
    assert cs.main(f.name) == 0
    try:
        with open(f.name, 'wb') as f:
            f.write(u'naïve\n'.encode('utf-8'))
        assert cs.main(f.name) == 0
        assert cs.main('-e', f.name) == 0
        with open(f.name, 'ab') as f:
            f.write(u'naieve\n'.encode('utf-8'))
        assert cs.main(f.name) == 1
        # Binary file warning
        with open(f.name, 'wb') as f:
            f.write(b'\x00\x00naiive\x00\x00')
        with CaptureStdout() as sio:
            assert cs.main(f.name) == 0
        assert 'WARNING: Binary file' in sio[1]
        with CaptureStdout() as sio:
            assert cs.main('-q', '2', f.name) == 0
        assert sio[1] == ''
    finally:
        os.remove(f.name)


def test_ignore():
    """Test ignoring of files and directories"""
    with TemporaryDirectory() as d:
        with open(op.join(d, 'good.txt'), 'w') as f:
            f.write('this file is okay')
        assert cs.main(d) == 0
        with open(op.join(d, 'bad.txt'), 'w') as f:
            f.write('abandonned')
        assert cs.main(d) == 1
        assert cs.main('--skip=bad*', d) == 0
        assert cs.main('--skip=bad.txt', d) == 0
        subdir = op.join(d, 'ignoredir')
        os.mkdir(subdir)
        with open(op.join(subdir, 'bad.txt'), 'w') as f:
            f.write('abandonned')
        assert cs.main(d) == 2
        assert cs.main('--skip=bad*', d) == 0
        assert cs.main('--skip=*ignoredir*', d) == 1
        assert cs.main('--skip=ignoredir', d) == 1


def test_check_filename():
    """Test filename check"""
    with TemporaryDirectory() as d:
        with open(op.join(d, 'abandonned.txt'), 'w') as f:
            f.write('.')
        assert cs.main('-f', d) == 1


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


def test_dictionary_formatting():
    """Test that all dictionary entries are in lower case and non-empty."""
    err_dict = dict()
    with open(op.join(op.dirname(__file__), '..', 'data',
                      'dictionary.txt'), 'rb') as fid:
        for line in fid:
            err, rep = line.decode('utf-8').split('->')
            err = err.lower()
            assert err not in err_dict, 'entry already exists'
            rep = rep.rstrip('\n')
            assert len(rep) > 0, 'corrections must be non-empty'
            if rep.count(','):
                if not rep.endswith(','):
                    assert 'disabled' in rep.split(',')[-1], \
                        ('currently corrections must end with trailing "," (if'
                         ' multiple corrections are available) or '
                         'have "disabled" in the comment')
            err_dict[err] = rep
            reps = [r.strip() for r in rep.lower().split(',')]
            reps = [r for r in reps if len(r)]
            unique = list()
            for r in reps:
                if r not in unique:
                    unique.append(r)
            assert reps == unique, 'entries are not (lower-case) unique'


def test_case_handling(reload_codespell_lib):
    """Test that capitalized entries get detected properly."""
    # Some simple Unicode things
    with tempfile.NamedTemporaryFile('wb') as f:
        pass
    # with CaptureStdout() as sio:
    assert cs.main(f.name) == 0
    try:
        with open(f.name, 'wb') as f:
            f.write('this has an ACII error'.encode('utf-8'))
        with CaptureStdout() as sio:
            assert cs.main(f.name) == 1
        assert 'ASCII' in sio[0]
        with CaptureStdout() as sio:
            assert cs.main('-w', f.name) == 0
        assert 'FIXED' in sio[1]
        with open(f.name, 'rb') as f:
            assert f.read().decode('utf-8') == 'this has an ASCII error'
    finally:
        os.remove(f.name)
