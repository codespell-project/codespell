# -*- coding: utf-8 -*-

from __future__ import print_function

import contextlib
import inspect
import os
import os.path as op
from shutil import copyfile
import subprocess
import sys

import pytest

import codespell_lib as cs_
from codespell_lib._codespell import EX_USAGE, EX_OK, EX_DATAERR


def test_constants():
    """Test our EX constants."""
    assert EX_OK == 0
    assert EX_USAGE == 64
    assert EX_DATAERR == 65


class MainWrapper(object):
    """Compatibility wrapper for when we used to return the count."""

    def main(self, *args, count=True, std=False, **kwargs):
        if count:
            args = ('--count',) + args
        code = cs_.main(*args, **kwargs)
        capsys = inspect.currentframe().f_back.f_locals['capsys']
        stdout, stderr = capsys.readouterr()
        assert code in (EX_OK, EX_USAGE, EX_DATAERR)
        if code == EX_DATAERR:  # have some misspellings
            code = int(stderr.split('\n')[-2])
        elif code == EX_OK and count:
            code = int(stderr.split('\n')[-2])
            assert code == 0
        if std:
            return (code, stdout, stderr)
        else:
            return code


cs = MainWrapper()


def run_codespell(args=(), cwd=None):
    """Run codespell."""
    args = ('--count',) + args
    proc = subprocess.Popen(
        ['codespell'] + list(args), cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stderr = proc.communicate()[1].decode('utf-8')
    count = int(stderr.split('\n')[-2])
    return count


def test_command(tmpdir):
    """Test running the codespell executable."""
    # With no arguments does "."
    d = str(tmpdir)
    assert run_codespell(cwd=d) == 0
    with open(op.join(d, 'bad.txt'), 'w') as f:
        f.write('abandonned\nAbandonned\nABANDONNED\nAbAnDoNnEd')
    assert run_codespell(cwd=d) == 4


def test_basic(tmpdir, capsys):
    """Test some basic functionality."""
    assert cs.main('_does_not_exist_') == 0
    fname = op.join(str(tmpdir), 'tmp')
    with open(fname, 'w') as f:
        pass
    code, _, stderr = cs.main('-D', 'foo', f.name, std=True)
    assert code == EX_USAGE, 'missing dictionary'
    assert 'cannot find dictionary' in stderr
    assert cs.main(fname) == 0, 'empty file'
    with open(fname, 'a') as f:
        f.write('this is a test file\n')
    assert cs.main(fname) == 0, 'good'
    with open(fname, 'a') as f:
        f.write('abandonned\n')
    assert cs.main(fname) == 1, 'bad'
    with open(fname, 'a') as f:
        f.write('abandonned\n')
    assert cs.main(fname) == 2, 'worse'
    with open(fname, 'a') as f:
        f.write('tim\ngonna\n')
    assert cs.main(fname) == 2, 'with a name'
    assert cs.main('--builtin', 'clear,rare,names,informal', fname) == 4
    code, _, stderr = cs.main(fname, '--builtin', 'foo', std=True)
    assert code == EX_USAGE  # bad type
    assert 'Unknown builtin dictionary' in stderr
    d = str(tmpdir)
    code, _, stderr = cs.main(fname, '-D', op.join(d, 'foo'), std=True)
    assert code == EX_USAGE  # bad dict
    assert 'cannot find dictionary' in stderr
    os.remove(fname)

    with open(op.join(d, 'bad.txt'), 'w') as f:
        f.write('abandonned\nAbandonned\nABANDONNED\nAbAnDoNnEd')
    assert cs.main(d) == 4
    code, _, stderr = cs.main('-w', d, std=True)
    assert code == 0
    assert 'FIXED:' in stderr
    with open(op.join(d, 'bad.txt')) as f:
        new_content = f.read()
    assert cs.main(d) == 0
    assert new_content == 'abandoned\nAbandoned\nABANDONED\nabandoned'

    with open(op.join(d, 'bad.txt'), 'w') as f:
        f.write('abandonned abandonned\n')
    assert cs.main(d) == 2
    code, stdout, stderr = cs.main(
        '-q', '16', '-w', d, count=False, std=True)
    assert code == 0
    assert stdout == stderr == ''
    assert cs.main(d) == 0

    # empty directory
    os.mkdir(op.join(d, 'test'))
    assert cs.main(d) == 0


def test_interactivity(tmpdir, capsys):
    """Test interaction"""
    # Windows can't read a currently-opened file, so here we use
    # NamedTemporaryFile just to get a good name
    with open(op.join(str(tmpdir), 'tmp'), 'w') as f:
        pass
    try:
        assert cs.main(f.name) == 0, 'empty file'
        with open(f.name, 'w') as f:
            f.write('abandonned\n')
        assert cs.main('-i', '-1', f.name) == 1, 'bad'
        with FakeStdin('y\n'):
            assert cs.main('-i', '3', f.name) == 1
        with FakeStdin('n\n'):
            code, stdout, _ = cs.main('-w', '-i', '3', f.name, std=True)
            assert code == 0
        assert '==>' in stdout
        with FakeStdin('x\ny\n'):
            assert cs.main('-w', '-i', '3', f.name) == 0
        assert cs.main(f.name) == 0
    finally:
        os.remove(f.name)

    # New example
    with open(op.join(str(tmpdir), 'tmp2'), 'w') as f:
        pass
    try:
        with open(f.name, 'w') as f:
            f.write('abandonned\n')
        assert cs.main(f.name) == 1
        with FakeStdin(' '):  # blank input -> Y
            assert cs.main('-w', '-i', '3', f.name) == 0
        assert cs.main(f.name) == 0
    finally:
        os.remove(f.name)

    # multiple options
    with open(op.join(str(tmpdir), 'tmp3'), 'w') as f:
        pass
    try:
        with open(f.name, 'w') as f:
            f.write('ackward\n')

        assert cs.main(f.name) == 1
        with FakeStdin(' \n'):  # blank input -> nothing
            assert cs.main('-w', '-i', '3', f.name) == 0
        assert cs.main(f.name) == 1
        with FakeStdin('0\n'):  # blank input -> nothing
            assert cs.main('-w', '-i', '3', f.name) == 0
        assert cs.main(f.name) == 0
        with open(f.name, 'r') as f_read:
            assert f_read.read() == 'awkward\n'
        with open(f.name, 'w') as f:
            f.write('ackward\n')
        assert cs.main(f.name) == 1
        with FakeStdin('x\n1\n'):  # blank input -> nothing
            code, stdout, _ = cs.main('-w', '-i', '3', f.name, std=True)
            assert code == 0
        assert 'a valid option' in stdout
        assert cs.main(f.name) == 0
        with open(f.name, 'r') as f:
            assert f.read() == 'backward\n'
    finally:
        os.remove(f.name)


def test_summary(tmpdir, capsys):
    """Test summary functionality."""
    with open(op.join(str(tmpdir), 'tmp'), 'w') as f:
        pass
    code, stdout, stderr = cs.main(f.name, std=True, count=False)
    assert code == 0
    assert stdout == stderr == '', 'no output'
    code, stdout, stderr = cs.main(f.name, '--summary', std=True)
    assert code == 0
    assert stderr == '0\n'
    assert 'SUMMARY' in stdout
    assert len(stdout.split('\n')) == 5
    with open(f.name, 'w') as f:
        f.write('abandonned\nabandonned')
    assert code == 0
    code, stdout, stderr = cs.main(f.name, '--summary', std=True)
    assert stderr == '2\n'
    assert 'SUMMARY' in stdout
    assert len(stdout.split('\n')) == 7
    assert 'abandonned' in stdout.split()[-2]


def test_ignore_dictionary(tmpdir, capsys):
    """Test ignore dictionary functionality."""
    d = str(tmpdir)
    with open(op.join(d, 'bad.txt'), 'w') as f:
        f.write('1 abandonned 1\n2 abandonned 2\nabondon\n')
    bad_name = f.name
    assert cs.main(bad_name) == 3
    with open(op.join(d, 'ignore.txt'), 'w') as f:
        f.write('abandonned\n')
    assert cs.main('-I', f.name, bad_name) == 1


def test_ignore_word_list(tmpdir, capsys):
    """Test ignore word list functionality."""
    d = str(tmpdir)
    with open(op.join(d, 'bad.txt'), 'w') as f:
        f.write('abandonned\nabondon\nabilty\n')
    assert cs.main(d) == 3
    assert cs.main('-Labandonned,someword', '-Labilty', d) == 1


def test_custom_regex(tmpdir, capsys):
    """Test custom word regex."""
    d = str(tmpdir)
    with open(op.join(d, 'bad.txt'), 'w') as f:
        f.write('abandonned_abondon\n')
    assert cs.main(d) == 0
    assert cs.main('-r', "[a-z]+", d) == 2
    code, stdout, _ = cs.main('-r', '[a-z]+', '--write-changes', d, std=True)
    assert code == EX_USAGE
    assert 'ERROR:' in stdout


def test_exclude_file(tmpdir, capsys):
    """Test exclude file functionality."""
    d = str(tmpdir)
    with open(op.join(d, 'bad.txt'), 'wb') as f:
        f.write('1 abandonned 1\n2 abandonned 2\n'.encode('utf-8'))
    bad_name = f.name
    assert cs.main(bad_name) == 2
    with open(op.join(d, 'tmp.txt'), 'wb') as f:
        f.write('1 abandonned 1\n'.encode('utf-8'))
    assert cs.main(bad_name) == 2
    assert cs.main('-x', f.name, bad_name) == 1


def test_encoding(tmpdir, capsys):
    """Test encoding handling."""
    # Some simple Unicode things
    with open(op.join(str(tmpdir), 'tmp'), 'w') as f:
        pass
    # with CaptureStdout() as sio:
    assert cs.main(f.name) == 0
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
    code, stdout, stderr = cs.main(f.name, std=True, count=False)
    assert code == 0
    assert stdout == stderr == ''
    code, stdout, stderr = cs.main('-q', '0', f.name, std=True, count=False)
    assert code == 0
    assert stdout == ''
    assert 'WARNING: Binary file' in stderr


def test_ignore(tmpdir, capsys):
    """Test ignoring of files and directories."""
    d = str(tmpdir)
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
    assert cs.main('--skip=*ignoredir/bad*', d) == 1


def test_check_filename(tmpdir, capsys):
    """Test filename check."""
    d = str(tmpdir)
    # Empty file
    with open(op.join(d, 'abandonned.txt'), 'w') as f:
        f.write('')
    assert cs.main('-f', d) == 1
    # Normal file with contents
    with open(op.join(d, 'abandonned.txt'), 'w') as f:
        f.write('.')
    assert cs.main('-f', d) == 1
    # Normal file with binary contents
    with open(op.join(d, 'abandonned.txt'), 'wb') as f:
        f.write(b'\x00\x00naiive\x00\x00')
    assert cs.main('-f', d) == 1


@pytest.mark.skipif((not hasattr(os, "mkfifo") or not callable(os.mkfifo)),
                    reason='requires os.mkfifo')
def test_check_filename_irregular_file(tmpdir, capsys):
    """Test irregular file filename check."""
    # Irregular file (!isfile())
    d = str(tmpdir)
    os.mkfifo(op.join(d, 'abandonned'))
    assert cs.main('-f', d) == 1
    d = str(tmpdir)


def test_check_hidden(tmpdir, capsys):
    """Test ignoring of hidden files."""
    d = str(tmpdir)
    # visible file
    with open(op.join(d, 'test.txt'), 'w') as f:
        f.write('abandonned\n')
    assert cs.main(op.join(d, 'test.txt')) == 1
    assert cs.main(d) == 1
    # hidden file
    os.rename(op.join(d, 'test.txt'), op.join(d, '.test.txt'))
    assert cs.main(op.join(d, '.test.txt')) == 0
    assert cs.main(d) == 0
    assert cs.main('--check-hidden', op.join(d, '.test.txt')) == 1
    assert cs.main('--check-hidden', d) == 1
    # hidden file with typo in name
    os.rename(op.join(d, '.test.txt'), op.join(d, '.abandonned.txt'))
    assert cs.main(op.join(d, '.abandonned.txt')) == 0
    assert cs.main(d) == 0
    assert cs.main('--check-hidden', op.join(d, '.abandonned.txt')) == 1
    assert cs.main('--check-hidden', d) == 1
    assert cs.main('--check-hidden', '--check-filenames',
                   op.join(d, '.abandonned.txt')) == 2
    assert cs.main('--check-hidden', '--check-filenames', d) == 2
    # hidden directory
    assert cs.main(d) == 0
    assert cs.main('--check-hidden', d) == 1
    assert cs.main('--check-hidden', '--check-filenames', d) == 2
    os.mkdir(op.join(d, '.abandonned'))
    copyfile(op.join(d, '.abandonned.txt'),
             op.join(d, '.abandonned', 'abandonned.txt'))
    assert cs.main(d) == 0
    assert cs.main('--check-hidden', d) == 2
    assert cs.main('--check-hidden', '--check-filenames', d) == 5


def test_case_handling(tmpdir, capsys):
    """Test that capitalized entries get detected properly."""
    # Some simple Unicode things
    with open(op.join(str(tmpdir), 'tmp'), 'w') as f:
        pass
    # with CaptureStdout() as sio:
    assert cs.main(f.name) == 0
    with open(f.name, 'wb') as f:
        f.write('this has an ACII error'.encode('utf-8'))
    code, stdout, _ = cs.main(f.name, std=True)
    assert code == 1
    assert 'ASCII' in stdout
    code, _, stderr = cs.main('-w', f.name, std=True)
    assert code == 0
    assert 'FIXED' in stderr
    with open(f.name, 'rb') as f:
        assert f.read().decode('utf-8') == 'this has an ASCII error'


def test_context(tmpdir, capsys):
    """Test context options."""
    d = str(tmpdir)
    with open(op.join(d, 'context.txt'), 'w') as f:
        f.write('line 1\nline 2\nline 3 abandonned\nline 4\nline 5')

    # symmetric context, fully within file
    code, stdout, _ = cs.main('-C', '1', d, std=True)
    assert code == 1
    lines = stdout.split('\n')
    assert len(lines) == 5
    assert lines[0] == ': line 2'
    assert lines[1] == '> line 3 abandonned'
    assert lines[2] == ': line 4'

    # requested context is bigger than the file
    code, stdout, _ = cs.main('-C', '10', d, std=True)
    assert code == 1
    lines = stdout.split('\n')
    assert len(lines) == 7
    assert lines[0] == ': line 1'
    assert lines[1] == ': line 2'
    assert lines[2] == '> line 3 abandonned'
    assert lines[3] == ': line 4'
    assert lines[4] == ': line 5'

    # only before context
    code, stdout, _ = cs.main('-B', '2', d, std=True)
    assert code == 1
    lines = stdout.split('\n')
    assert len(lines) == 5
    assert lines[0] == ': line 1'
    assert lines[1] == ': line 2'
    assert lines[2] == '> line 3 abandonned'

    # only after context
    code, stdout, _ = cs.main('-A', '1', d, std=True)
    assert code == 1
    lines = stdout.split('\n')
    assert len(lines) == 4
    assert lines[0] == '> line 3 abandonned'
    assert lines[1] == ': line 4'

    # asymmetric context
    code, stdout, _ = cs.main('-B', '2', '-A', '1', d, std=True)
    assert code == 1
    lines = stdout.split('\n')
    assert len(lines) == 6
    assert lines[0] == ': line 1'
    assert lines[1] == ': line 2'
    assert lines[2] == '> line 3 abandonned'
    assert lines[3] == ': line 4'

    # both '-C' and '-A' on the command line
    code, stdout, _ = cs.main('-C', '2', '-A', '1', d, std=True)
    assert code == EX_USAGE
    lines = stdout.split('\n')
    assert 'ERROR' in lines[0]

    # both '-C' and '-B' on the command line
    code, stdout, stderr = cs.main('-C', '2', '-B', '1', d, std=True)
    assert code == EX_USAGE
    lines = stdout.split('\n')
    assert 'ERROR' in lines[0]


def test_ignore_regex_flag(tmpdir, capsys):
    """Test ignore regex flag functionality."""
    d = str(tmpdir)

    # Invalid regex.
    code, stdout, _ = cs.main('--ignore-regex=(', std=True)
    assert code == EX_USAGE
    assert 'usage:' in stdout

    with open(op.join(d, 'flag.txt'), 'w') as f:
        f.write('# Please see http://example.com/abandonned for info\n')
    # Test file has 1 invalid entry, and it's not ignored by default.
    assert cs.main(f.name) == 1
    # An empty regex is the default value, and nothing is ignored.
    assert cs.main(f.name, '--ignore-regex=') == 1
    assert cs.main(f.name, '--ignore-regex=""') == 1
    # Non-matching regex results in nothing being ignored.
    assert cs.main(f.name, '--ignore-regex=^$') == 1
    # A word can be ignored.
    assert cs.main(f.name, '--ignore-regex=abandonned') == 0
    # Ignoring part of the word can result in odd behavior.
    assert cs.main(f.name, '--ignore-regex=nn') == 0

    with open(op.join(d, 'flag.txt'), 'w') as f:
        f.write('abandonned donn\n')
    # Test file has 2 invalid entries.
    assert cs.main(f.name) == 2
    # Ignoring donn breaks them both.
    assert cs.main(f.name, '--ignore-regex=donn') == 0
    # Adding word breaks causes only one to be ignored.
    assert cs.main(f.name, r'--ignore-regex=\Wdonn\W') == 1


def test_config(tmpdir, capsys):
    """
    Tests loading options from a config file.
    """
    d = str(tmpdir)

    # Create sample files.
    with open(op.join(d, 'bad.c'), 'w') as f:
        f.write('abandonned donn\n')
    with open(op.join(d, 'good.c'), 'w') as f:
        f.write("good")

    # Create a config file.
    with open(op.join(d, 'config.cfg'), 'w') as f:
        f.write(
            '[tool:codespell]\n'
            'skip = *bad.c,*config.cfg\n'
            'count = \n'
        )

    # Should fail when checking both.
    code, stdout, _ = cs.main(count=False, std=True)
    assert code == EX_DATAERR
    assert 'bad.c' in stdout

    # Should pass when skipping bad.c
    code, stdout, _ = cs.main('--config config.cfg', count=False, std=True)
    assert code == EX_OK
    assert 'bad.c' not in stdout


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
