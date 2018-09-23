# -*- coding: utf-8 -*-

import os.path as op
import re


def test_dictionary_formatting():
    """Test that all dictionary entries are valid."""
    err_dict = dict()
    ws = re.compile(r'.*\s.*')  # whitespace
    comma = re.compile(r'.*,.*')  # comma
    with open(op.join(op.dirname(__file__), '..', 'data',
                      'dictionary.txt'), 'rb') as fid:
        for line in fid:
            err, rep = line.decode('utf-8').split('->')
            err = err.lower()
            assert err not in err_dict, 'error %r already exists' % err
            assert ws.match(err) is None, 'error %r has whitespace' % err
            assert comma.match(err) is None, 'error %r has a comma' % err
            rep = rep.rstrip('\n')
            assert len(rep) > 0, ('error %s: correction %r must be non-empty'
                                  % (err, rep))
            assert not re.match(r'^\s.*', rep), ('error %s: correction %r '
                                                 'cannot start with whitespace'
                                                 % (err, rep))
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
