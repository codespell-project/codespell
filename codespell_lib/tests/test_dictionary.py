# -*- coding: utf-8 -*-

import glob
import os.path as op
import os
import re
import warnings

import pytest

from codespell_lib._codespell import _builtin_dictionaries

try:
    import aspell
    speller = aspell.Speller('lang', 'en')
except Exception as exp:  # probably ImportError, but maybe also language
    speller = None
    if os.getenv('REQUIRE_ASPELL', 'false').lower() == 'true':
        raise RuntimeError(
            'Cannot run complete tests without aspell when '
            'REQUIRE_ASPELL=true. Got error during import:\n%s'
            % (exp,))
    else:
        warnings.warn(
            'aspell not found, but not required, skipping aspell tests. Got '
            'error during import:\n%s' % (exp,))

ws = re.compile(r'.*\s.*')  # whitespace
comma = re.compile(r'.*,.*')  # comma

global_err_dicts = dict()

# Filename, should be seen as errors in aspell or not
_data_dir = op.join(op.dirname(__file__), '..', 'data')
_fnames_in_aspell = [
    (op.join(_data_dir, 'dictionary%s.txt' % d[2]), d[3:5])
    for d in _builtin_dictionaries]
fname_params = pytest.mark.parametrize('fname, in_aspell', _fnames_in_aspell)


def test_dictionaries_exist():
    """Test consistency of dictionaries."""
    doc_fnames = set(op.basename(f[0]) for f in _fnames_in_aspell)
    got_fnames = set(op.basename(f)
                     for f in glob.glob(op.join(_data_dir, '*.txt')))
    assert doc_fnames == got_fnames


@fname_params
def test_dictionary_formatting(fname, in_aspell):
    """Test that all dictionary entries are valid."""
    errors = list()
    with open(fname, 'rb') as fid:
        for line in fid:
            err, rep = line.decode('utf-8').split('->')
            err = err.lower()
            rep = rep.rstrip('\n')
            try:
                _check_err_rep(err, rep, in_aspell, fname)
            except AssertionError as exp:
                errors.append(str(exp).split('\n')[0])
    if len(errors):
        raise AssertionError('\n' + '\n'.join(errors))


def _check_aspell(phrase, msg, in_aspell, fname):
    if speller is None:
        return  # cannot check
    if in_aspell is None:
        return  # don't check
    if ' ' in phrase:
        for word in phrase.split():
            _check_aspell(word, msg, in_aspell, fname)
        return  # stop normal checking as we've done each word above
    this_in_aspell = speller.check(
        phrase.encode(speller.ConfigKeys()['encoding'][1]))
    end = 'be in aspell for dictionary %s' % (fname,)
    if in_aspell:  # should be an error in aspell
        assert this_in_aspell, '%s should %s' % (msg, end)
    else:  # shouldn't be
        assert not this_in_aspell, '%s should not %s' % (msg, end)


def _check_err_rep(err, rep, in_aspell, fname):
    assert ws.match(err) is None, 'error %r has whitespace' % err
    assert comma.match(err) is None, 'error %r has a comma' % err
    assert len(rep) > 0, ('error %s: correction %r must be non-empty'
                          % (err, rep))
    assert not re.match(r'^\s.*', rep), ('error %s: correction %r '
                                         'cannot start with whitespace'
                                         % (err, rep))
    _check_aspell(err, 'error %r' % (err,), in_aspell[0], fname)
    prefix = 'error %s: correction %r' % (err, rep)
    for (r, msg) in [
            (r'^,',
             '%s starts with a comma'),
            (r'\s,',
             '%s contains a whitespace character followed by a comma'),
            (r',\s\s',
             '%s contains a comma followed by multiple whitespace characters'),
            (r',[^ ]',
             '%s contains a comma *not* followed by a space'),
            (r'\s+$',
             '%s has a trailing space'),
            (r'^[^,]*,\s*$',
             '%s has a single entry but contains a trailing comma')]:
        assert not re.search(r, rep), (msg % (prefix,))
    del msg
    if rep.count(','):
        assert rep.endswith(','), ('error %s: multiple corrections must end '
                                   'with trailing ","' % (err,))
    reps = [r.strip() for r in rep.lower().split(',')]
    reps = [r for r in reps if len(r)]
    for r in reps:
        assert err != r.lower(), ('error %r corrects to itself amongst others'
                                  % (err,))
        _check_aspell(
            r, 'error %s: correction %r' % (err, r), in_aspell[1], fname)
    assert len(set(reps)) == len(reps), ('error %s: corrections "%s" are not '
                                         '(lower-case) unique' % (err, rep))


@pytest.mark.parametrize('err, rep, match', [
    ('a a', 'bar', 'has whitespace'),
    ('a,a', 'bar', 'has a comma'),
    ('a', '', 'non-empty'),
    ('a', ' bar', 'start with whitespace'),
    ('a', ',bar', 'starts with a comma'),
    ('a', 'bar,bat', '.*not.*followed by a space'),
    ('a', 'bar ', 'trailing space'),
    ('a', 'b ,ar', 'contains a whitespace.*followed by a comma'),
    ('a', 'bar,', 'single entry.*comma'),
    ('a', 'bar, bat', 'must end with trailing ","'),
    ('a', 'a, bar,', 'corrects to itself amongst others'),
    ('a', 'a', 'corrects to itself'),
    ('a', 'bar, bar,', 'unique'),
])
def test_error_checking(err, rep, match):
    """Test that our error checking works."""
    with pytest.raises(AssertionError, match=match):
        _check_err_rep(err, rep, (None, None), 'dummy')


@pytest.mark.skipif(speller is None, reason='requires aspell')
@pytest.mark.parametrize('err, rep, err_aspell, rep_aspell, match', [
    # This doesn't raise any exceptions, so skip for now:
    # pytest.param('a', 'uvw, bar,', None, None, 'should be in aspell'),
    ('abcdef', 'uvwxyz, bar,', True, None, 'should be in aspell'),
    ('a', 'uvwxyz, bar,', False, None, 'should not be in aspell'),
    ('a', 'abcdef, uvwxyz,', None, True, 'should be in aspell'),
    ('abcdef', 'uvwxyz, bar,', True, True, 'should be in aspell'),
    ('abcdef', 'uvwxyz, bar,', False, True, 'should be in aspell'),
    ('a', 'bar, back,', None, False, 'should not be in aspell'),
    ('abcdef', 'ghijkl, uvwxyz,', True, False, 'should be in aspell'),
    ('abcdef', 'uvwxyz, bar,', False, False, 'should not be in aspell'),
    # Multi-word corrections
    # One multi-word, both parts
    ('a', 'abcdef uvwxyz', None, True, 'should be in aspell'),
    ('a', 'bar back', None, False, 'should not be in aspell'),
    # Second multi-word, both parts
    ('a', 'bar back, abcdef uvwxyz, bar,', None, True, 'should be in aspell'),
    ('a', 'abcdef uvwxyz, bar back, ghijkl,', None, False, 'should not be in aspell'),  # noqa: E501
    # One multi-word, second part
    ('a', 'bar abcdef', None, True, 'should be in aspell'),
    ('a', 'abcdef back', None, False, 'should not be in aspell'),
])
def test_error_checking_in_aspell(err, rep, err_aspell, rep_aspell, match):
    """Test that our error checking works with aspell."""
    with pytest.raises(AssertionError, match=match):
        _check_err_rep(err, rep, (err_aspell, rep_aspell), 'dummy')


@fname_params
def test_dictionary_looping(fname, in_aspell):
    """Test that all dictionary entries are valid."""
    global_err_dicts[fname] = dict()
    file_err_dict = dict()
    with open(fname, 'rb') as fid:
        for line in fid:
            err, rep = line.decode('utf-8').split('->')
            err = err.lower()
            assert err not in file_err_dict, 'error %r already exists in %s' % (err, fname)
            # We check if it's in file_err_dict too, so we don't throw two errors when it is
            assert (err in file_err_dict) or (err not in global_err_dict), 'error %r already exists in another dictionary file' % (err)
            rep = rep.rstrip('\n')
            reps = [r.strip() for r in rep.lower().split(',')]
            reps = [r for r in reps if len(r)]
            file_err_dict[err] = reps
            global_err_dicts[fname][err] = reps
    # check for corrections that are themselves errors
    for err in file_err_dict:
        for r in file_err_dict[err]:
            assert r not in file_err_dict, \
                ('error %s: correction %s is an error itself in %s' % (err, r, fname))
    # check for corrections that are themselves errors in other dictionaries
    for other_fname, global_err_dict in global_err_dicts.items():
        for err in global_err_dict:
            for r in global_err_dict[err]:
                assert (r in file_err_dict) or (r not in global_err_dict), \
                    ('error %s: correction %s is an error itself in %s' % (err, r, other_fname))
            
