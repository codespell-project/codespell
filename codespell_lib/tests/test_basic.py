# -*- coding: utf-8 -*-

import contextlib
import inspect
import os
import os.path as op
import re
from shutil import copyfile
import subprocess
import sys

import pytest

import codespell_lib as cs_
from codespell_lib._codespell import uri_regex_def, EX_USAGE, EX_OK, EX_DATAERR


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

    with open(op.join(d, 'bad.txt'), 'w', newline='') as f:
        f.write('abandonned\nAbandonned\nABANDONNED\nAbAnDoNnEd\nabandonned\rAbandonned\r\nABANDONNED \n AbAnDoNnEd')  # noqa: E501
    assert cs.main(d) == 8
    code, _, stderr = cs.main('-w', d, std=True)
    assert code == 0
    assert 'FIXED:' in stderr
    with open(op.join(d, 'bad.txt'), newline='') as f:
        new_content = f.read()
    assert cs.main(d) == 0
    assert new_content == 'abandoned\nAbandoned\nABANDONED\nabandoned\nabandoned\rAbandoned\r\nABANDONED \n abandoned'  # noqa: E501

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
    code, _, stderr = cs.main('-r', '[a-z]+', '--write-changes', d, std=True)
    assert code == EX_USAGE
    assert 'ERROR:' in stderr


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
    # Encoding detection (only try ISO 8859-1 because UTF-8 is the default)
    with open(f.name, 'wb') as f:
        f.write(b'Speling error, non-ASCII: h\xe9t\xe9rog\xe9n\xe9it\xe9\n')
    # check warnings about wrong encoding are enabled with "-q 0"
    code, stdout, stderr = cs.main('-q', '0', f.name, std=True, count=True)
    assert code == 1
    assert 'Speling' in stdout
    assert 'iso-8859-1' in stderr
    # check warnings about wrong encoding are disabled with "-q 1"
    code, stdout, stderr = cs.main('-q', '1', f.name, std=True, count=True)
    assert code == 1
    assert 'Speling' in stdout
    assert 'iso-8859-1' not in stderr
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
    goodtxt = op.join(d, 'good.txt')
    with open(goodtxt, 'w') as f:
        f.write('this file is okay')
    assert cs.main(d) == 0
    badtxt = op.join(d, 'bad.txt')
    with open(badtxt, 'w') as f:
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
    badjs = op.join(d, 'bad.js')
    copyfile(badtxt, badjs)
    assert cs.main('--skip=*.js', goodtxt, badtxt, badjs) == 1


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


def _helper_test_case_handling_in_fixes(tmpdir, capsys, reason):
    d = str(tmpdir)

    with open(op.join(d, 'dictionary.txt'), 'w') as f:
        if reason:
            f.write('adoptor->adopter, adaptor, reason\n')
        else:
            f.write('adoptor->adopter, adaptor,\n')
    dictionary_name = f.name

    # the mispelled word is entirely lowercase
    with open(op.join(d, 'bad.txt'), 'w') as f:
        f.write('early adoptor\n')
    code, stdout, _ = cs.main('-D', dictionary_name, f.name, std=True)
    # all suggested fixes must be lowercase too
    assert 'adopter, adaptor' in stdout
    # the reason, if any, must not be modified
    if reason:
        assert 'reason' in stdout

    # the mispelled word is capitalized
    with open(op.join(d, 'bad.txt'), 'w') as f:
        f.write('Early Adoptor\n')
    code, stdout, _ = cs.main('-D', dictionary_name, f.name, std=True)
    # all suggested fixes must be capitalized too
    assert 'Adopter, Adaptor' in stdout
    # the reason, if any, must not be modified
    if reason:
        assert 'reason' in stdout

    # the mispelled word is entirely uppercase
    with open(op.join(d, 'bad.txt'), 'w') as f:
        f.write('EARLY ADOPTOR\n')
    code, stdout, _ = cs.main('-D', dictionary_name, f.name, std=True)
    # all suggested fixes must be uppercase too
    assert 'ADOPTER, ADAPTOR' in stdout
    # the reason, if any, must not be modified
    if reason:
        assert 'reason' in stdout

    # the mispelled word mixes lowercase and uppercase
    with open(op.join(d, 'bad.txt'), 'w') as f:
        f.write('EaRlY AdOpToR\n')
    code, stdout, _ = cs.main('-D', dictionary_name, f.name, std=True)
    # all suggested fixes should be lowercase
    assert 'adopter, adaptor' in stdout
    # the reason, if any, must not be modified
    if reason:
        assert 'reason' in stdout


def test_case_handling_in_fixes(tmpdir, capsys):
    """Test that the case of fixes is similar to the mispelled word."""
    _helper_test_case_handling_in_fixes(tmpdir, capsys, reason=False)
    _helper_test_case_handling_in_fixes(tmpdir, capsys, reason=True)


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
    code, _, stderr = cs.main('-C', '2', '-A', '1', d, std=True)
    assert code == EX_USAGE
    lines = stderr.split('\n')
    assert 'ERROR' in lines[0]

    # both '-C' and '-B' on the command line
    code, _, stderr = cs.main('-C', '2', '-B', '1', d, std=True)
    assert code == EX_USAGE
    lines = stderr.split('\n')
    assert 'ERROR' in lines[0]


def test_ignore_regex_option(tmpdir, capsys):
    """Test ignore regex option functionality."""
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
    assert cs.main(f.name, r'--ignore-regex=\bdonn\b') == 1


def test_uri_regex_option(tmpdir, capsys):
    """Test --uri-regex option functionality."""
    d = str(tmpdir)

    # Invalid regex.
    code, stdout, _ = cs.main('--uri-regex=(', std=True)
    assert code == EX_USAGE
    assert 'usage:' in stdout

    with open(op.join(d, 'flag.txt'), 'w') as f:
        f.write('# Please see http://abandonned.com for info\n')

    # By default, the standard regex is used.
    assert cs.main(f.name) == 1
    assert cs.main(f.name, '--uri-ignore-words-list=abandonned') == 0

    # If empty, nothing matches.
    assert cs.main(f.name, '--uri-regex=',
                   '--uri-ignore-words-list=abandonned') == 0

    # Can manually match urls.
    assert cs.main(f.name, '--uri-regex=\\bhttp.*\\b',
                   '--uri-ignore-words-list=abandonned') == 0

    # Can also match arbitrary content.
    with open(op.join(d, 'flag.txt'), 'w') as f:
        f.write('abandonned')
    assert cs.main(f.name) == 1
    assert cs.main(f.name, '--uri-ignore-words-list=abandonned') == 1
    assert cs.main(f.name, '--uri-regex=.*') == 1
    assert cs.main(f.name, '--uri-regex=.*',
                   '--uri-ignore-words-list=abandonned') == 0


def test_uri_ignore_words_list_option_uri(tmpdir, capsys):
    """Test ignore regex option functionality."""
    d = str(tmpdir)

    with open(op.join(d, 'flag.txt'), 'w') as f:
        f.write('# Please see http://example.com/abandonned for info\n')
    # Test file has 1 invalid entry, and it's not ignored by default.
    assert cs.main(f.name) == 1
    # An empty list is the default value, and nothing is ignored.
    assert cs.main(f.name, '--uri-ignore-words-list=') == 1
    # Non-matching regex results in nothing being ignored.
    assert cs.main(f.name, '--uri-ignore-words-list=foo,example') == 1
    # A word can be ignored.
    assert cs.main(f.name, '--uri-ignore-words-list=abandonned') == 0
    assert cs.main(f.name, '--uri-ignore-words-list=foo,abandonned,bar') == 0
    assert cs.main(f.name, '--uri-ignore-words-list=*') == 0
    # The match must be for the complete word.
    assert cs.main(f.name, '--uri-ignore-words-list=abandonn') == 1

    with open(op.join(d, 'flag.txt'), 'w') as f:
        f.write('abandonned http://example.com/abandonned\n')
    # Test file has 2 invalid entries.
    assert cs.main(f.name) == 2
    # Ignoring the value in the URI won't ignore the word completely.
    assert cs.main(f.name, '--uri-ignore-words-list=abandonned') == 1
    assert cs.main(f.name, '--uri-ignore-words-list=*') == 1
    # The regular --ignore-words-list will ignore both.
    assert cs.main(f.name, '--ignore-words-list=abandonned') == 0

    variation_option = '--uri-ignore-words-list=abandonned'

    # Variations where an error is ignored.
    for variation in ('# Please see http://abandonned for info\n',
                      '# Please see "http://abandonned" for info\n',
                      # This variation could be un-ignored, but it'd require a
                      # more complex regex as " is valid in parts of URIs.
                      '# Please see "http://foo"abandonned for info\n',
                      '# Please see https://abandonned for info\n',
                      '# Please see ftp://abandonned for info\n',
                      '# Please see http://example/abandonned for info\n',
                      '# Please see http://example.com/abandonned for info\n',
                      '# Please see http://exam.com/ple#abandonned for info\n',
                      '# Please see http://exam.com/ple?abandonned for info\n',
                      '# Please see http://127.0.0.1/abandonned for info\n',
                      '# Please see http://[2001:0db8:85a3:0000:0000:8a2e:0370'
                      ':7334]/abandonned for info\n'):
        with open(op.join(d, 'flag.txt'), 'w') as f:
            f.write(variation)
        assert cs.main(f.name) == 1, variation
        assert cs.main(f.name, variation_option) == 0, variation

    # Variations where no error is ignored.
    for variation in ('# Please see abandonned/ for info\n',
                      '# Please see http:abandonned for info\n',
                      '# Please see foo/abandonned for info\n',
                      '# Please see http://foo abandonned for info\n'):
        with open(op.join(d, 'flag.txt'), 'w') as f:
            f.write(variation)
        assert cs.main(f.name) == 1, variation
        assert cs.main(f.name, variation_option) == 1, variation


def test_uri_ignore_words_list_option_email(tmpdir, capsys):
    """Test ignore regex option functionality."""
    d = str(tmpdir)

    with open(op.join(d, 'flag.txt'), 'w') as f:
        f.write('# Please see example@abandonned.com for info\n')
    # Test file has 1 invalid entry, and it's not ignored by default.
    assert cs.main(f.name) == 1
    # An empty list is the default value, and nothing is ignored.
    assert cs.main(f.name, '--uri-ignore-words-list=') == 1
    # Non-matching regex results in nothing being ignored.
    assert cs.main(f.name, '--uri-ignore-words-list=foo,example') == 1
    # A word can be ignored.
    assert cs.main(f.name, '--uri-ignore-words-list=abandonned') == 0
    assert cs.main(f.name, '--uri-ignore-words-list=foo,abandonned,bar') == 0
    assert cs.main(f.name, '--uri-ignore-words-list=*') == 0
    # The match must be for the complete word.
    assert cs.main(f.name, '--uri-ignore-words-list=abandonn') == 1

    with open(op.join(d, 'flag.txt'), 'w') as f:
        f.write('abandonned example@abandonned.com\n')
    # Test file has 2 invalid entries.
    assert cs.main(f.name) == 2
    # Ignoring the value in the URI won't ignore the word completely.
    assert cs.main(f.name, '--uri-ignore-words-list=abandonned') == 1
    assert cs.main(f.name, '--uri-ignore-words-list=*') == 1
    # The regular --ignore-words-list will ignore both.
    assert cs.main(f.name, '--ignore-words-list=abandonned') == 0

    variation_option = '--uri-ignore-words-list=abandonned'

    # Variations where an error is ignored.
    for variation in ('# Please see example@abandonned for info\n',
                      '# Please see abandonned@example for info\n',
                      '# Please see abandonned@example.com for info\n',
                      '# Please see mailto:abandonned@example.com?subject=Test'
                      ' for info\n'):
        with open(op.join(d, 'flag.txt'), 'w') as f:
            f.write(variation)
        assert cs.main(f.name) == 1, variation
        assert cs.main(f.name, variation_option) == 0, variation

    # Variations where no error is ignored.
    for variation in ('# Please see example @ abandonned for info\n',
                      '# Please see abandonned@ example for info\n',
                      '# Please see mailto:foo@example.com?subject=Test'
                      ' abandonned for info\n'):
        with open(op.join(d, 'flag.txt'), 'w') as f:
            f.write(variation)
        assert cs.main(f.name) == 1, variation
        assert cs.main(f.name, variation_option) == 1, variation


def test_uri_regex_def():
    uri_regex = re.compile(uri_regex_def)

    # Tests based on https://mathiasbynens.be/demo/url-regex
    true_positives = (
        'http://foo.com/blah_blah',
        'http://foo.com/blah_blah/',
        'http://foo.com/blah_blah_(wikipedia)',
        'http://foo.com/blah_blah_(wikipedia)_(again)',
        'http://www.example.com/wpstyle/?p=364',
        'https://www.example.com/foo/?bar=baz&inga=42&quux',
        'http://✪df.ws/123',
        'http://userid:password@example.com:8080',
        'http://userid:password@example.com:8080/',
        'http://userid@example.com',
        'http://userid@example.com/',
        'http://userid@example.com:8080',
        'http://userid@example.com:8080/',
        'http://userid:password@example.com',
        'http://userid:password@example.com/',
        'http://142.42.1.1/',
        'http://142.42.1.1:8080/',
        'http://➡.ws/䨹',
        'http://⌘.ws',
        'http://⌘.ws/',
        'http://foo.com/blah_(wikipedia)#cite-1',
        'http://foo.com/blah_(wikipedia)_blah#cite-1',
        'http://foo.com/unicode_(✪)_in_parens',
        'http://foo.com/(something)?after=parens',
        'http://☺.damowmow.com/',
        'http://code.google.com/events/#&product=browser',
        'http://j.mp',
        'ftp://foo.bar/baz',
        'http://foo.bar/?q=Test%20URL-encoded%20stuff',
        'http://مثال.إختبار',
        'http://例子.测试',
        'http://उदाहरण.परीक्षा',
        "http://-.~_!$&'()*+,;=:%40:80%2f::::::@example.com",
        'http://1337.net',
        'http://a.b-c.de',
        'http://223.255.255.254',
    )
    true_negatives = (
        'http://',
        '//',
        '//a',
        '///a',
        '///',
        'foo.com',
        'rdar://1234',
        'h://test',
        '://should.fail',
        'ftps://foo.bar/',
    )
    false_positives = (
        'http://.',
        'http://..',
        'http://../',
        'http://?',
        'http://??',
        'http://??/',
        'http://#',
        'http://##',
        'http://##/',
        'http:///a',
        'http://-error-.invalid/',
        'http://a.b--c.de/',
        'http://-a.b.co',
        'http://a.b-.co',
        'http://0.0.0.0',
        'http://10.1.1.0',
        'http://10.1.1.255',
        'http://224.1.1.1',
        'http://1.1.1.1.1',
        'http://123.123.123',
        'http://3628126748',
        'http://.www.foo.bar/',
        'http://www.foo.bar./',
        'http://.www.foo.bar./',
        'http://10.1.1.1',
    )

    boilerplate = 'Surrounding text %s more text'

    for uri in true_positives + false_positives:
        assert uri_regex.findall(uri) == [uri], uri
        assert uri_regex.findall(boilerplate % uri) == [uri], uri

    for uri in true_negatives:
        assert not uri_regex.findall(uri), uri
        assert not uri_regex.findall(boilerplate % uri), uri


@pytest.mark.parametrize('kind', ('toml', 'cfg'))
def test_config_toml(tmp_path, capsys, kind):
    """Test loading options from a config file or toml."""
    d = tmp_path / 'files'
    d.mkdir()
    with open(d / 'bad.txt', 'w') as f:
        f.write('abandonned donn\n')
    with open(d / 'good.txt', 'w') as f:
        f.write("good")

    # Should fail when checking both.
    code, stdout, _ = cs.main(str(d), count=True, std=True)
    # Code in this case is not exit code, but count of misspellings.
    assert code == 2
    assert 'bad.txt' in stdout

    if kind == 'cfg':
        conffile = str(tmp_path / 'setup.cfg')
        args = ('--config', conffile)
        with open(conffile, 'w') as f:
            f.write("""\
[codespell]
skip = bad.txt, whatever.txt
count =
""")
    else:
        assert kind == 'toml'
        pytest.importorskip('tomli')
        tomlfile = str(tmp_path / 'pyproject.toml')
        args = ('--toml', tomlfile)
        with open(tomlfile, 'w') as f:
            f.write("""\
[tool.codespell]
skip = 'bad.txt,whatever.txt'
count = false
""")

    # Should pass when skipping bad.txt
    code, stdout, _ = cs.main(str(d), *args, count=True, std=True)
    assert code == 0
    assert 'bad.txt' not in stdout

    # And both should automatically work if they're in cwd
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        code, stdout, _ = cs.main(str(d), count=True, std=True)
    finally:
        os.chdir(cwd)
    assert code == 0
    assert 'bad.txt' not in stdout


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
