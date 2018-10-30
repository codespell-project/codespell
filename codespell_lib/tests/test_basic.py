# -*- coding: utf-8 -*-

from __future__ import print_function

import contextlib
import os
import os.path as op
import subprocess
import sys

import codespell_lib as cs


def run_codespell(args=(), cwd=None):
    """Helper to run codespell"""
    return subprocess.Popen(
        ['codespell'] + list(args), cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()


def test_command(tmpdir):
    """Test running the codespell executable"""
    # With no arguments does "."
    d = str(tmpdir)
    assert run_codespell(cwd=d) == 0
    with open(op.join(d, 'bad.txt'), 'w') as f:
        f.write('abandonned\nAbandonned\nABANDONNED\nAbAnDoNnEd')
    assert run_codespell(cwd=d) == 4


def test_basic(tmpdir, capsys):
    """Test some basic functionality"""
    assert cs.main('_does_not_exist_') == 0
    with open(op.join(str(tmpdir), 'tmp'), 'w') as f:
        pass
    assert cs.main('-D', 'foo', f.name) == 1, 'missing dictionary'
    try:
        assert 'cannot find dictionary' in capsys.readouterr()[1]
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
    d = str(tmpdir)
    with open(op.join(d, 'bad.txt'), 'w') as f:
        f.write('abandonned\nAbandonned\nABANDONNED\nAbAnDoNnEd')
    assert cs.main(d) == 4
    capsys.readouterr()
    assert cs.main('-w', d) == 0
    assert 'FIXED:' in capsys.readouterr()[1]
    with open(op.join(d, 'bad.txt')) as f:
        new_content = f.read()
    assert cs.main(d) == 0
    assert new_content == 'abandoned\nAbandoned\nABANDONED\nabandoned'

    with open(op.join(d, 'bad.txt'), 'w') as f:
        f.write('abandonned abandonned\n')
    assert cs.main(d) == 2
    capsys.readouterr()
    assert cs.main('-q', '16', '-w', d) == 0
    assert capsys.readouterr() == ('', '')
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
            assert cs.main('-w', '-i', '3', f.name) == 0
        assert '==>' in capsys.readouterr()[0]
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
        capsys.readouterr()
        with FakeStdin('x\n1\n'):  # blank input -> nothing
            assert cs.main('-w', '-i', '3', f.name) == 0
        assert 'a valid option' in capsys.readouterr()[0]
        assert cs.main(f.name) == 0
        with open(f.name, 'r') as f:
            assert f.read() == 'backward\n'
    finally:
        os.remove(f.name)


def test_summary(tmpdir, capsys):
    """Test summary functionality"""
    with open(op.join(str(tmpdir), 'tmp'), 'w') as f:
        pass
    try:
        cs.main(f.name)
        assert capsys.readouterr() == ('', ''), 'no output'
        cs.main(f.name, '--summary')
        stdout, stderr = capsys.readouterr()
        assert stderr == ''
        assert 'SUMMARY' in stdout
        assert len(stdout.split('\n')) == 5
        with open(f.name, 'w') as f:
            f.write('abandonned\nabandonned')
        cs.main(f.name, '--summary')
        stdout, stderr = capsys.readouterr()
        assert stderr == ''
        assert 'SUMMARY' in stdout
        assert len(stdout.split('\n')) == 7
        assert 'abandonned' in stdout.split()[-2]
    finally:
        os.remove(f.name)


def test_ignore_dictionary(tmpdir):
    """Test ignore dictionary functionality."""
    d = str(tmpdir)
    with open(op.join(d, 'bad.txt'), 'w') as f:
        f.write('1 abandonned 1\n2 abandonned 2\nabondon\n')
    bad_name = f.name
    assert cs.main(bad_name) == 3
    with open(op.join(d, 'ignore.txt'), 'w') as f:
        f.write('abandonned\n')
    assert cs.main('-I', f.name, bad_name) == 1


def test_ignore_word_list(tmpdir):
    """Test ignore word list functionality"""
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
    capsys.readouterr()
    assert cs.main('-r', '[a-z]+', '--write-changes', d) == 1
    assert 'ERROR:' in capsys.readouterr()[0]


def test_exclude_file(tmpdir):
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
        capsys.readouterr()
        assert cs.main(f.name) == 0
        assert 'WARNING: Binary file' in capsys.readouterr()[1]
        assert cs.main('-q', '2', f.name) == 0
        assert capsys.readouterr() == ('', '')
    finally:
        os.remove(f.name)


def test_ignore(tmpdir):
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


def test_check_filename(tmpdir):
    """Test filename check."""
    d = str(tmpdir)
    with open(op.join(d, 'abandonned.txt'), 'w') as f:
        f.write('.')
    assert cs.main('-f', d) == 1


def test_check_hidden(tmpdir):
    """Test ignoring of hidden files."""
    d = str(tmpdir)
    # hidden file
    with open(op.join(d, 'test.txt'), 'w') as f:
        f.write('abandonned\n')
    assert cs.main(op.join(d, 'test.txt')) == 1
    os.rename(op.join(d, 'test.txt'), op.join(d, '.test.txt'))
    assert cs.main(op.join(d, '.test.txt')) == 0
    assert cs.main('--check-hidden', op.join(d, '.test.txt')) == 1
    os.rename(op.join(d, '.test.txt'), op.join(d, '.abandonned.txt'))
    assert cs.main(op.join(d, '.abandonned.txt')) == 0
    assert cs.main('--check-hidden', op.join(d, '.abandonned.txt')) == 1
    assert cs.main('--check-hidden', '--check-filenames',
                   op.join(d, '.abandonned.txt')) == 2


def test_case_handling(tmpdir, capsys):
    """Test that capitalized entries get detected properly."""
    # Some simple Unicode things
    with open(op.join(str(tmpdir), 'tmp'), 'w') as f:
        pass
    # with CaptureStdout() as sio:
    assert cs.main(f.name) == 0
    try:
        with open(f.name, 'wb') as f:
            f.write('this has an ACII error'.encode('utf-8'))
        assert cs.main(f.name) == 1
        assert 'ASCII' in capsys.readouterr()[0]
        assert cs.main('-w', f.name) == 0
        assert 'FIXED' in capsys.readouterr()[1]
        with open(f.name, 'rb') as f:
            assert f.read().decode('utf-8') == 'this has an ASCII error'
    finally:
        os.remove(f.name)


def test_context(tmpdir, capsys):
    """Test context options."""
    d = str(tmpdir)
    with open(op.join(d, 'context.txt'), 'w') as f:
        f.write('line 1\nline 2\nline 3 abandonned\nline 4\nline 5')

    # symmetric context, fully within file
    cs.main('-C', '1', d)
    lines = capsys.readouterr()[0].split('\n')
    assert len(lines) == 5
    assert lines[0] == ': line 2'
    assert lines[1] == '> line 3 abandonned'
    assert lines[2] == ': line 4'

    # requested context is bigger than the file
    cs.main('-C', '10', d)
    lines = capsys.readouterr()[0].split('\n')
    assert len(lines) == 7
    assert lines[0] == ': line 1'
    assert lines[1] == ': line 2'
    assert lines[2] == '> line 3 abandonned'
    assert lines[3] == ': line 4'
    assert lines[4] == ': line 5'

    # only before context
    cs.main('-B', '2', d)
    lines = capsys.readouterr()[0].split('\n')
    assert len(lines) == 5
    assert lines[0] == ': line 1'
    assert lines[1] == ': line 2'
    assert lines[2] == '> line 3 abandonned'

    # only after context
    cs.main('-A', '1', d)
    lines = capsys.readouterr()[0].split('\n')
    assert len(lines) == 4
    assert lines[0] == '> line 3 abandonned'
    assert lines[1] == ': line 4'

    # asymmetric context
    cs.main('-B', '2', '-A', '1', d)
    lines = capsys.readouterr()[0].split('\n')
    assert len(lines) == 6
    assert lines[0] == ': line 1'
    assert lines[1] == ': line 2'
    assert lines[2] == '> line 3 abandonned'
    assert lines[3] == ': line 4'

    # both '-C' and '-A' on the command line
    cs.main('-C', '2', '-A', '1', d)
    lines = capsys.readouterr()[0].split('\n')
    assert 'ERROR' in lines[0]

    # both '-C' and '-B' on the command line
    cs.main('-C', '2', '-B', '1', d)
    lines = capsys.readouterr()[0].split('\n')
    assert 'ERROR' in lines[0]


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
