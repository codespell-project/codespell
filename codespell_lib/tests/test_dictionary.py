# -*- coding: utf-8 -*-

import glob
import os.path as op
import os
import re
import warnings

import pytest

from codespell_lib._codespell import _builtin_dictionaries
from codespell_lib._codespell import supported_languages

spellers = dict()

try:
    import aspell
    for lang in supported_languages:
        spellers[lang] = aspell.Speller('lang', lang)
except Exception as exp:  # probably ImportError, but maybe also language
    if os.getenv('REQUIRE_ASPELL', 'false').lower() == 'true':
        raise RuntimeError(
            'Cannot run complete tests without aspell when '
            'REQUIRE_ASPELL=true. Got error during import:\n%s'
            % (exp,))
    else:
        warnings.warn(
            'aspell not found, but not required, skipping aspell tests. Got '
            'error during import:\n%s' % (exp,))

global_err_dicts = dict()
global_pairs = set()

# Filename, should be seen as errors in aspell or not
_data_dir = op.join(op.dirname(__file__), '..', 'data')
_fnames_in_aspell = [
    (op.join(_data_dir, 'dictionary%s.txt' % d[2]), d[3:5], d[5:7])
    for d in _builtin_dictionaries]
fname_params = pytest.mark.parametrize('fname, in_aspell, in_dictionary', _fnames_in_aspell)  # noqa: E501


def test_dictionaries_exist():
    """Test consistency of dictionaries."""
    doc_fnames = set(op.basename(f[0]) for f in _fnames_in_aspell)
    got_fnames = set(op.basename(f)
                     for f in glob.glob(op.join(_data_dir, '*.txt')))
    assert doc_fnames == got_fnames


@fname_params
def test_dictionary_formatting(fname, in_aspell, in_dictionary):
    """Test that all dictionary entries are valid."""
    errors = list()
    with open(fname, 'rb') as fid:
        for line in fid:
            err, rep = line.decode('utf-8').split('->')
            err = err.lower()
            rep = rep.rstrip('\n')
            try:
                _check_err_rep(err, rep, in_aspell, fname, in_dictionary)
            except AssertionError as exp:
                errors.append(str(exp).split('\n')[0])
    if len(errors):
        raise AssertionError('\n' + '\n'.join(errors))


def _check_aspell(phrase, msg, in_aspell, fname, languages):
    if not spellers:  # if no spellcheckers exist
        return  # cannot check
    if in_aspell is None:
        return  # don't check
    if ' ' in phrase:
        for word in phrase.split():
            _check_aspell(word, msg, in_aspell, fname, languages)
        return  # stop normal checking as we've done each word above
    this_in_aspell = any(spellers[lang].check(phrase.encode(
        spellers[lang].ConfigKeys()['encoding'][1])) for lang in languages)
    end = 'be in aspell dictionaries (%s) for dictionary %s' % (
        ', '.join(languages), fname)
    if in_aspell:  # should be an error in aspell
        assert this_in_aspell, '%s should %s' % (msg, end)
    else:  # shouldn't be
        assert not this_in_aspell, '%s should not %s' % (msg, end)


whitespace = re.compile(r'\s')
start_whitespace = re.compile(r'^\s')
start_comma = re.compile(r'^,')
whitespace_comma = re.compile(r'\s,')
comma_whitespaces = re.compile(r',\s\s')
comma_without_space = re.compile(r',[^ ]')
whitespace_end = re.compile(r'\s+$')
single_comma = re.compile(r'^[^,]*,\s*$')


def _check_err_rep(err, rep, in_aspell, fname, languages):
    assert whitespace.search(err) is None, 'error %r has whitespace' % err
    assert ',' not in err, 'error %r has a comma' % err
    assert len(rep) > 0, ('error %s: correction %r must be non-empty'
                          % (err, rep))
    assert not start_whitespace.match(rep), ('error %s: correction %r '
                                             'cannot start with whitespace'
                                             % (err, rep))
    _check_aspell(err, 'error %r' % (err,), in_aspell[0], fname, languages[0])
    prefix = 'error %s: correction %r' % (err, rep)
    for (r, msg) in [
            (start_comma,
             '%s starts with a comma'),
            (whitespace_comma,
             '%s contains a whitespace character followed by a comma'),
            (comma_whitespaces,
             '%s contains a comma followed by multiple whitespace characters'),
            (comma_without_space,
             '%s contains a comma *not* followed by a space'),
            (whitespace_end,
             '%s has a trailing space'),
            (single_comma,
             '%s has a single entry but contains a trailing comma')]:
        assert not r.search(rep), (msg % (prefix,))
    del msg
    if rep.count(','):
        assert rep.endswith(','), ('error %s: multiple corrections must end '
                                   'with trailing ","' % (err,))
    reps = [r.strip() for r in rep.split(',')]
    reps = [r for r in reps if len(r)]
    for r in reps:
        assert err != r.lower(), ('error %r corrects to itself amongst others'
                                  % (err,))
        _check_aspell(
            r, 'error %s: correction %r' % (err, r),
            in_aspell[1], fname, languages[1])

    # aspell dictionary is case sensitive, so pass the original case into there
    # we could ignore the case, but that would miss things like days of the
    # week which we want to be correct
    reps = [r.lower() for r in reps]
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
    ('a', 'bar, Bar,', 'unique'),
])
def test_error_checking(err, rep, match):
    """Test that our error checking works."""
    with pytest.raises(AssertionError, match=match):
        _check_err_rep(err, rep, (None, None), 'dummy',
                       (supported_languages, supported_languages))


@pytest.mark.skipif(not spellers, reason='requires aspell-en')
@pytest.mark.parametrize('err, rep, err_aspell, rep_aspell, match', [
    # This doesn't raise any exceptions, so skip for now:
    # pytest.param('a', 'uvw, bar,', None, None, 'should be in aspell'),
    ('abcdef', 'uvwxyz, bar,', True, None, 'should be in aspell'),
    ('a', 'uvwxyz, bar,', False, None, 'should not be in aspell'),
    ('a', 'abcdef, uvwxyz,', None, True, 'should be in aspell'),
    ('abcdef', 'uvwxyz, bar,', True, True, 'should be in aspell'),
    ('abcdef', 'uvwxyz, bar,', False, True, 'should be in aspell'),
    ('a', 'bar, back,', None, False, 'should not be in aspell'),
    ('a', 'bar, back, Wednesday,', None, False, 'should not be in aspell'),
    ('abcdef', 'ghijkl, uvwxyz,', True, False, 'should be in aspell'),
    ('abcdef', 'uvwxyz, bar,', False, False, 'should not be in aspell'),
    # Multi-word corrections
    # One multi-word, both parts
    ('a', 'abcdef uvwxyz', None, True, 'should be in aspell'),
    ('a', 'bar back', None, False, 'should not be in aspell'),
    ('a', 'bar back Wednesday', None, False, 'should not be in aspell'),
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
        _check_err_rep(
            err, rep, (err_aspell, rep_aspell), 'dummy',
            (supported_languages, supported_languages))


# allow some duplicates, like "m-i-n-i-m-i-s-e", or "c-a-l-c-u-l-a-t-a-b-l-e"
# correction in left can appear as typo in right
allowed_dups = {
    ('dictionary.txt', 'dictionary_code.txt'),
    ('dictionary.txt', 'dictionary_en-GB_to_en-US.txt'),
    ('dictionary.txt', 'dictionary_names.txt'),
    ('dictionary.txt', 'dictionary_rare.txt'),
    ('dictionary.txt', 'dictionary_usage.txt'),
    ('dictionary_code.txt', 'dictionary_rare.txt'),
    ('dictionary_rare.txt', 'dictionary_usage.txt'),
}


@fname_params
@pytest.mark.dependency(name='dictionary loop')
def test_dictionary_looping(fname, in_aspell, in_dictionary):
    """Test that all dictionary entries are valid."""
    this_err_dict = dict()
    short_fname = op.basename(fname)
    with open(fname, 'rb') as fid:
        for line in fid:
            err, rep = line.decode('utf-8').split('->')
            err = err.lower()
            assert err not in this_err_dict, \
                'error %r already exists in %s' % (err, short_fname)
            rep = rep.rstrip('\n')
            reps = [r.strip() for r in rep.lower().split(',')]
            reps = [r for r in reps if len(r)]
            this_err_dict[err] = reps
    # 1. check the dict against itself (diagonal)
    for err in this_err_dict:
        for r in this_err_dict[err]:
            assert r not in this_err_dict, \
                ('error %s: correction %s is an error itself in the same '
                 'dictionary file %s' % (err, r, short_fname))
    pair = (short_fname, short_fname)
    assert pair not in global_pairs
    global_pairs.add(pair)
    for other_fname, other_err_dict in global_err_dicts.items():
        # error duplication (eventually maybe we should just merge?)
        for err in this_err_dict:
            assert err not in other_err_dict, \
                ('error %r in dictionary %s already exists in dictionary '
                 '%s' % (err, short_fname, other_fname))
        # 2. check corrections in this dict against other dicts (upper)
        pair = (short_fname, other_fname)
        if pair not in allowed_dups:
            for err in this_err_dict:
                assert err not in other_err_dict, \
                    ('error %r in dictionary %s already exists in dictionary '
                     '%s' % (err, short_fname, other_fname))
                for r in this_err_dict[err]:
                    assert r not in other_err_dict, \
                        ('error %s: correction %s from dictionary %s is an '
                         'error itself in dictionary %s'
                         % (err, r, short_fname, other_fname))
        assert pair not in global_pairs
        global_pairs.add(pair)
        # 3. check corrections in other dicts against this dict (lower)
        pair = (other_fname, short_fname)
        if pair not in allowed_dups:
            for err in other_err_dict:
                for r in other_err_dict[err]:
                    assert r not in this_err_dict, \
                        ('error %s: correction %s from dictionary %s is an '
                         'error itself in dictionary %s'
                         % (err, r, other_fname, short_fname))
        assert pair not in global_pairs
        global_pairs.add(pair)
    global_err_dicts[short_fname] = this_err_dict


@pytest.mark.dependency(depends=['dictionary loop'])
def test_ran_all():
    """Test that all pairwise tests ran."""
    for f1, _, _ in _fnames_in_aspell:
        f1 = op.basename(f1)
        for f2, _, _ in _fnames_in_aspell:
            f2 = op.basename(f2)
            assert (f1, f2) in global_pairs
    assert len(global_pairs) == len(_fnames_in_aspell) ** 2
