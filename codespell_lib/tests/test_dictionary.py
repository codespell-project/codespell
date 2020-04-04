# -*- coding: utf-8 -*-

import glob
import os.path as op
import re
import pytest
from codespell_lib._codespell import _builtin_dictionaries

try:
    import aspell
    speller = aspell.Speller('lang', 'en')
except Exception:  # probably ImportError, but maybe also language
    speller = None

ws = re.compile(r'.*\s.*')  # whitespace
comma = re.compile(r'.*,.*')  # comma


# Filename, should be seen as errors in aspell or not
_data_dir = op.join(op.dirname(__file__), '..', 'data')
_fnames_in_aspell = [
    (op.join(_data_dir, 'dictionary%s.txt' % d[2]), d[3])
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
            except Exception as exp:
                errors.append(str(exp).split('\n')[0])
    if len(errors):
        raise AssertionError('\n' + '\n'.join(errors))


def _check_err_rep(err, rep, in_aspell, fname):
    assert err != rep.lower(), 'error %r corrects to itself' % err
    assert ws.match(err) is None, 'error %r has whitespace' % err
    assert comma.match(err) is None, 'error %r has a comma' % err
    assert len(rep) > 0, ('error %s: correction %r must be non-empty'
                          % (err, rep))
    assert not re.match(r'^\s.*', rep), ('error %s: correction %r '
                                         'cannot start with whitespace'
                                         % (err, rep))
    if speller is not None:
        this_in_aspell = speller.check(
            err.encode(speller.ConfigKeys()['encoding'][1]))
        if not in_aspell:
            assert not this_in_aspell, ('error %r should not be in aspell '
                                        'for dictionary %s' % (err, fname))
    prefix = 'error %s: correction %r' % (err, rep)
    for (r, msg) in [
            (r'^,',
             '%s starts with a comma'),
            (r'\s,',
             '%s contains a whitespace character followed by a comma'),
            (r',\s\s',
             '%s contains a comma followed by multiple whitespace '
             'characters'),
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
    unique = list()
    for r in reps:
        if r not in unique:
            unique.append(r)
    assert reps == unique, 'entries are not (lower-case) unique'


@fname_params
def test_dictionary_looping(fname, in_aspell):
    """Test that all dictionary entries are valid."""
    err_dict = dict()
    with open(fname, 'rb') as fid:
        for line in fid:
            err, rep = line.decode('utf-8').split('->')
            err = err.lower()
            assert err not in err_dict, 'error %r already exists' % err
            rep = rep.rstrip('\n')
            reps = [r.strip() for r in rep.lower().split(',')]
            reps = [r for r in reps if len(r)]
            err_dict[err] = reps
    # check for corrections that are errors (but not self replacements)
    for err in err_dict:
        for r in err_dict[err]:
            assert (r not in err_dict) or (r in err_dict[r]), \
                ('error %s: correction %s is an error itself' % (err, r))
