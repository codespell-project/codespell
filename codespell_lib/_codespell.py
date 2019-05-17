# -*- coding: utf-8 -*-
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.html.
"""
Copyright (C) 2010-2011  Lucas De Marchi <lucas.de.marchi@gmail.com>
Copyright (C) 2011  ProFUSION embedded systems
"""

from __future__ import print_function

import codecs
import sys
import re
from optparse import OptionParser
import os
import fnmatch

word_regex_def = u"[\\w\\-'’`]+"
encodings = ('utf-8', 'iso-8859-1')
USAGE = """
\t%prog [OPTIONS] [file1 file2 ... fileN]
"""
VERSION = '1.15.0'

# Users might want to link this file into /usr/local/bin, so we resolve the
# symbolic link path to the real path if necessary.
default_dictionary = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                  'data', 'dictionary.txt')

# OPTIONS:
#
# ARGUMENTS:
#    dict_filename       The file containing the dictionary of misspellings.
#                        If set to '-', it will be read from stdin
#    file1 .. fileN      Files to check spelling


class QuietLevels(object):
    NONE = 0
    ENCODING = 1
    BINARY_FILE = 2
    DISABLED_FIXES = 4
    NON_AUTOMATIC_FIXES = 8
    FIXES = 16


class GlobMatch(object):
    def __init__(self, pattern):
        if pattern:
            self.pattern_list = pattern.split(',')
        else:
            self.pattern_list = None

    def match(self, filename):
        if self.pattern_list is None:
            return False

        for p in self.pattern_list:
            if fnmatch.fnmatch(filename, p):
                return True

        return False


class Misspelling(object):
    def __init__(self, data, fix, reason):
        self.data = data
        self.fix = fix
        self.reason = reason


class TermColors(object):
    def __init__(self):
        self.FILE = '\033[33m'
        self.WWORD = '\033[31m'
        self.FWORD = '\033[32m'
        self.DISABLE = '\033[0m'

    def disable(self):
        self.FILE = ''
        self.WWORD = ''
        self.FWORD = ''
        self.DISABLE = ''


class Summary(object):
    def __init__(self):
        self.summary = {}

    def update(self, wrongword):
        if wrongword in self.summary:
            self.summary[wrongword] += 1
        else:
            self.summary[wrongword] = 1

    def __str__(self):
        keys = list(self.summary.keys())
        keys.sort()

        return "\n".join(["{0}{1:{width}}".format(
                         key,
                         self.summary.get(key),
                         width=15 - len(key)) for key in keys])


class FileOpener(object):
    def __init__(self, use_chardet, quiet_level):
        self.use_chardet = use_chardet
        if use_chardet:
            self.init_chardet()
        self.quiet_level = quiet_level

    def init_chardet(self):
        try:
            from chardet.universaldetector import UniversalDetector
        except ImportError:
            raise ImportError("There's no chardet installed to import from. "
                              "Please, install it and check your PYTHONPATH "
                              "environment variable")

        self.encdetector = UniversalDetector()

    def open(self, filename):
        if self.use_chardet:
            return self.open_with_chardet(filename)
        else:
            return self.open_with_internal(filename)

    def open_with_chardet(self, filename):
        self.encdetector.reset()
        with codecs.open(filename, 'rb') as f:
            for line in f:
                self.encdetector.feed(line)
                if self.encdetector.done:
                    break
        self.encdetector.close()
        encoding = self.encdetector.result['encoding']

        try:
            f = codecs.open(filename, 'r', encoding=encoding)
        except UnicodeDecodeError:
            print('ERROR: Could not detect encoding: %s' % filename,
                  file=sys.stderr)
            raise
        except LookupError:
            print('ERROR: %s -- Don\'t know how to handle encoding %s'
                  % (filename, encoding), file=sys.stderr)
            raise
        else:
            lines = f.readlines()
            f.close()

        return lines, encoding

    def open_with_internal(self, filename):
        curr = 0
        while True:
            try:
                f = codecs.open(filename, 'r', encoding=encodings[curr])
            except UnicodeDecodeError:
                if not self.quiet_level & QuietLevels.ENCODING:
                    print('WARNING: Decoding file %s' % filename,
                          file=sys.stderr)
                    print('WARNING: using encoding=%s failed. '
                          % encodings[curr], file=sys.stderr)
                    try:
                        print('WARNING: Trying next encoding: %s'
                              % encodings[curr + 1], file=sys.stderr)
                    except IndexError:
                        pass

                curr += 1
            else:
                lines = f.readlines()
                f.close()
                break
        if not lines:
            raise Exception('Unknown encoding')

        encoding = encodings[curr]

        return lines, encoding

# -.-:-.-:-.-:-.:-.-:-.-:-.-:-.-:-.:-.-:-.-:-.-:-.-:-.:-.-:-


def parse_options(args):
    parser = OptionParser(usage=USAGE, version=VERSION)

    parser.set_defaults(colors=sys.stdout.isatty())
    parser.add_option('-d', '--disable-colors',
                      action='store_false', dest='colors',
                      help='disable colors even when printing to terminal '
                      '(always on for Windows)')
    parser.add_option('-c', '--enable-colors',
                      action='store_true', dest='colors',
                      help='enable colors even when not printing to terminal')
    parser.add_option('-w', '--write-changes',
                      action='store_true', default=False,
                      help='write changes in place if possible')
    parser.add_option('-D', '--dictionary',
                      action='append', metavar='FILE',
                      help='Custom dictionary file that contains spelling '
                           'corrections. If this flag is not specified or '
                           'equals "-" then the default dictionary is used. '
                           'This option can be specified multiple times.')
    parser.add_option('-I', '--ignore-words',
                      action='append', metavar='FILE',
                      help='File that contains words which will be ignored '
                           'by codespell. File must contain 1 word per line. '
                           'Words are case sensitive based on how they are '
                           'written in codespell_lib/data/dictionary.txt')
    parser.add_option('-L', '--ignore-words-list',
                      action='append', metavar='WORDS',
                      help='Comma separated list of words to be ignored '
                           'by codespell. Words are case sensitive based on '
                           'how they are written in '
                           'codespell_lib/data/dictionary.txt')
    parser.add_option('-r', '--regex',
                      action='store', type='string',
                      help='Regular expression which is used to find words. '
                           'By default any alphanumeric character, the '
                           'underscore, the hyphen, and the apostrophe is '
                           'used to build words (i.e. %s). This option cannot '
                           'be specified together with the write-changes '
                           'functionality. ' % word_regex_def)
    parser.add_option('-s', '--summary',
                      action='store_true', default=False,
                      help='print summary of fixes')

    parser.add_option('-S', '--skip',
                      help='Comma-separated list of files to skip. It '
                           'accepts globs as well. E.g.: if you want '
                           'codespell to skip .eps and .txt files, '
                           'you\'d give "*.eps,*.txt" to this option.')

    parser.add_option('-x', '--exclude-file',
                      help='FILE with lines that should not be changed',
                      metavar='FILE')

    parser.add_option('-i', '--interactive',
                      action='store', type='int', default=0,
                      help='Set interactive mode when writing changes. '
                           '0 is the same as no interactivity; 1 makes '
                           'codespell ask for confirmation; 2 ask user to '
                           'choose one fix when more than one is '
                           'available; 3 applies both 1 and 2')

    parser.add_option('-q', '--quiet-level',
                      action='store', type='int', default=0,
                      help='Bitmask that allows codespell to run quietly. '
                           '0: the default, in which all messages are '
                           'printed. 1: disable warnings about wrong '
                           'encoding. 2: disable warnings about binary '
                           'file. 4: shut down warnings about automatic '
                           'fixes that were disabled in dictionary. '
                           '8: don\'t print anything for non-automatic '
                           'fixes. 16: don\'t print fixed files.')

    parser.add_option('-e', '--hard-encoding-detection',
                      action='store_true', default=False,
                      help='Use chardet to detect the encoding of each '
                           'file. This can slow down codespell, but is more '
                           'reliable in detecting encodings other than utf-8, '
                           'iso8859-1 and ascii.')

    parser.add_option('-f', '--check-filenames',
                      action='store_true', default=False,
                      help='Check file names as well.')

    parser.add_option('-H', '--check-hidden',
                      action='store_true', default=False,
                      help='Check hidden files (those starting with ".") as '
                           'well.')
    parser.add_option('-A', '--after-context', metavar='LINES',
                      help='print LINES of trailing context', type='int')
    parser.add_option('-B', '--before-context', metavar='LINES',
                      help='print LINES of leading context', type='int')
    parser.add_option('-C', '--context', metavar='LINES',
                      help='print LINES of surrounding context', type='int')

    (o, args) = parser.parse_args(list(args))

    if not args:
        args.append('.')

    return o, args, parser


def build_exclude_hashes(filename, exclude_lines):
    with codecs.open(filename, 'r') as f:
        for line in f:
            exclude_lines.add(line)


def build_ignore_words(filename, ignore_words):
    with codecs.open(filename, mode='r', buffering=1, encoding='utf-8') as f:
        for line in f:
            ignore_words.add(line.strip())


def build_dict(filename, misspellings, ignore_words):
    with codecs.open(filename, mode='r', buffering=1, encoding='utf-8') as f:
        for line in f:
            [key, data] = line.split('->')
            # TODO for now, convert both to lower. Someday we can maybe add
            # support for fixing caps.
            key = key.lower()
            data = data.lower()
            if key in ignore_words:
                continue
            data = data.strip()
            fix = data.rfind(',')

            if fix < 0:
                fix = True
                reason = ''
            elif fix == (len(data) - 1):
                data = data[:fix]
                reason = ''
                fix = False
            else:
                reason = data[fix + 1:].strip()
                data = data[:fix]
                fix = False

            misspellings[key] = Misspelling(data, fix, reason)


def is_hidden(filename, check_hidden):
    bfilename = os.path.basename(filename)

    if bfilename != '' and bfilename != '.' and bfilename != '..' \
                    and (not check_hidden and bfilename[0] == '.'):
        return True

    return False


def is_text_file(filename):
    with open(filename, mode='rb') as f:
        s = f.read(1024)
    if b'\x00' in s:
        return False
    return True


def fix_case(word, fixword):
    if word == word.capitalize():
        return fixword.capitalize()
    elif word == word.upper():
        return fixword.upper()
    # they are both lower case
    # or we don't have any idea
    return fixword


def ask_for_word_fix(line, wrongword, misspelling, interactivity):
    if interactivity <= 0:
        return misspelling.fix, fix_case(wrongword, misspelling.data)

    if misspelling.fix and interactivity & 1:
        r = ''
        fixword = fix_case(wrongword, misspelling.data)
        while not r:
            print("%s\t%s  ==> %s (Y/n) " % (line, wrongword, fixword), end='')
            r = sys.stdin.readline().strip().upper()
            if not r:
                r = 'Y'
            if r != 'Y' and r != 'N':
                print("Say 'y' or 'n'")
                r = ''

        if r == 'N':
            misspelling.fix = False
            misspelling.fixword = ''

    elif (interactivity & 2) and not misspelling.reason:
        # if it is not disabled, i.e. it just has more than one possible fix,
        # we ask the user which word to use

        r = ''
        opt = list(map(lambda x: x.strip(), misspelling.data.split(',')))
        while not r:
            print("%s Choose an option (blank for none): " % line, end='')
            for i in range(len(opt)):
                fixword = fix_case(wrongword, opt[i])
                print(" %d) %s" % (i, fixword), end='')
            print(": ", end='')
            sys.stdout.flush()

            n = sys.stdin.readline().strip()
            if not n:
                break

            try:
                n = int(n)
                r = opt[n]
            except (ValueError, IndexError):
                print("Not a valid option\n")

        if r:
            misspelling.fix = True
            misspelling.data = r

    return misspelling.fix, fix_case(wrongword, misspelling.data)


def print_context(lines, index, context):
    # context = (context_before, context_after)
    for i in range(index - context[0], index + context[1] + 1):
        if 0 <= i < len(lines):
            print('%s %s' % ('>' if i == index else ':', lines[i].rstrip()))


def parse_file(filename, colors, summary, misspellings, exclude_lines,
               file_opener, word_regex, context, options):
    bad_count = 0
    lines = None
    changed = False
    encoding = encodings[0]  # if not defined, use UTF-8

    if filename == '-':
        f = sys.stdin
        lines = f.readlines()
    else:
        # ignore binary files
        if not os.path.isfile(filename):
            return 0
        if options.check_filenames:
            for word in word_regex.findall(filename):
                lword = word.lower()
                if lword not in misspellings:
                    continue
                fix = misspellings[lword].fix
                fixword = fix_case(word, misspellings[lword].data)

                if summary and fix:
                    summary.update(lword)

                cfilename = "%s%s%s" % (colors.FILE, filename, colors.DISABLE)
                cwrongword = "%s%s%s" % (colors.WWORD, word, colors.DISABLE)
                crightword = "%s%s%s" % (colors.FWORD, fixword, colors.DISABLE)

                if misspellings[lword].reason:
                    if options.quiet_level & QuietLevels.DISABLED_FIXES:
                        continue
                    creason = "  | %s%s%s" % (colors.FILE,
                                              misspellings[lword].reason,
                                              colors.DISABLE)
                else:
                    if options.quiet_level & QuietLevels.NON_AUTOMATIC_FIXES:
                        continue
                    creason = ''

                bad_count += 1

                print("%(FILENAME)s: %(WRONGWORD)s "
                      " ==> %(RIGHTWORD)s%(REASON)s"
                      % {'FILENAME': cfilename,
                         'WRONGWORD': cwrongword,
                         'RIGHTWORD': crightword, 'REASON': creason})

        text = is_text_file(filename)
        if not text:
            if not options.quiet_level & QuietLevels.BINARY_FILE:
                print("WARNING: Binary file: %s " % filename, file=sys.stderr)
            return 0
        try:
            lines, encoding = file_opener.open(filename)
        except Exception:
            return 0

    for i, line in enumerate(lines):
        if line in exclude_lines:
            continue

        fixed_words = set()
        asked_for = set()

        for word in word_regex.findall(line):
            lword = word.lower()
            if lword in misspellings:
                context_shown = False
                fix = misspellings[lword].fix
                fixword = fix_case(word, misspellings[lword].data)

                if options.interactive and lword not in asked_for:
                    if context is not None:
                        context_shown = True
                        print_context(lines, i, context)
                    fix, fixword = ask_for_word_fix(
                        lines[i], word, misspellings[lword],
                        options.interactive)
                    asked_for.add(lword)

                if summary and fix:
                    summary.update(lword)

                if word in fixed_words:  # can skip because of re.sub below
                    continue

                if options.write_changes and fix:
                    changed = True
                    lines[i] = re.sub(r'\b%s\b' % word, fixword, lines[i])
                    fixed_words.add(word)
                    continue

                # otherwise warning was explicitly set by interactive mode
                if (options.interactive & 2 and not fix and not
                        misspellings[lword].reason):
                    continue

                cfilename = "%s%s%s" % (colors.FILE, filename, colors.DISABLE)
                cline = "%s%d%s" % (colors.FILE, i + 1, colors.DISABLE)
                cwrongword = "%s%s%s" % (colors.WWORD, word, colors.DISABLE)
                crightword = "%s%s%s" % (colors.FWORD, fixword, colors.DISABLE)

                if misspellings[lword].reason:
                    if options.quiet_level & QuietLevels.DISABLED_FIXES:
                        continue

                    creason = "  | %s%s%s" % (colors.FILE,
                                              misspellings[lword].reason,
                                              colors.DISABLE)
                else:
                    if options.quiet_level & QuietLevels.NON_AUTOMATIC_FIXES:
                        continue

                    creason = ''

                # If we get to this point (uncorrected error) we should change
                # our bad_count and thus return value
                bad_count += 1

                if (not context_shown) and (context is not None):
                    print_context(lines, i, context)
                if filename != '-':
                    print("%(FILENAME)s:%(LINE)s: %(WRONGWORD)s "
                          " ==> %(RIGHTWORD)s%(REASON)s"
                          % {'FILENAME': cfilename, 'LINE': cline,
                             'WRONGWORD': cwrongword,
                             'RIGHTWORD': crightword, 'REASON': creason})
                else:
                    print('%(LINE)s: %(STRLINE)s\n\t%(WRONGWORD)s '
                          '==> %(RIGHTWORD)s%(REASON)s'
                          % {'LINE': cline, 'STRLINE': line.strip(),
                             'WRONGWORD': cwrongword,
                             'RIGHTWORD': crightword, 'REASON': creason})

    if changed:
        if filename == '-':
            print("---")
            for line in lines:
                print(line, end='')
        else:
            if not options.quiet_level & QuietLevels.FIXES:
                print("%sFIXED:%s %s"
                      % (colors.FWORD, colors.DISABLE, filename),
                      file=sys.stderr)
            with codecs.open(filename, 'w', encoding=encoding) as f:
                f.writelines(lines)
    return bad_count


def _script_main():
    """Wrap to main() for setuptools."""
    return main(*sys.argv[1:])


def main(*args):
    """Contains flow control"""
    options, args, parser = parse_options(args)

    if options.regex and options.write_changes:
        print('ERROR: --write-changes cannot be used together with '
              '--regex')
        parser.print_help()
        return 1
    word_regex = options.regex or word_regex_def
    try:
        word_regex = re.compile(word_regex)
    except re.error as err:
        print('ERROR: invalid regular expression "%s" (%s)' %
              (word_regex, err), file=sys.stderr)
        parser.print_help()
        return 1

    ignore_words_files = options.ignore_words or []
    ignore_words = set()
    for ignore_words_file in ignore_words_files:
        if not os.path.exists(ignore_words_file):
            print('ERROR: cannot find ignore-words file: %s' %
                  ignore_words_file, file=sys.stderr)
            parser.print_help()
            return 1
        build_ignore_words(ignore_words_file, ignore_words)

    ignore_words_list = options.ignore_words_list or []
    for comma_separated_words in ignore_words_list:
        for word in comma_separated_words.split(','):
            ignore_words.add(word.strip())

    dictionaries = options.dictionary or [default_dictionary]
    misspellings = dict()
    for dictionary in dictionaries:
        if dictionary == "-":
            dictionary = default_dictionary
        if not os.path.exists(dictionary):
            print('ERROR: cannot find dictionary file: %s' % dictionary,
                  file=sys.stderr)
            parser.print_help()
            return 1
        build_dict(dictionary, misspellings, ignore_words)
    colors = TermColors()
    if not options.colors or sys.platform == 'win32':
        colors.disable()

    if options.summary:
        summary = Summary()
    else:
        summary = None

    context = None
    if options.context is not None:
        if (options.before_context is not None) or \
                (options.after_context is not None):
            print('ERROR: --context/-C cannot be used together with '
                  '--context-before/-B or --context-after/-A')
            parser.print_help()
            return 1
        context_both = max(0, options.context)
        context = (context_both, context_both)
    elif (options.before_context is not None) or \
            (options.after_context is not None):
        context_before = 0
        context_after = 0
        if options.before_context is not None:
            context_before = max(0, options.before_context)
        if options.after_context is not None:
            context_after = max(0, options.after_context)
        context = (context_before, context_after)

    exclude_lines = set()
    if options.exclude_file:
        build_exclude_hashes(options.exclude_file, exclude_lines)

    file_opener = FileOpener(options.hard_encoding_detection,
                             options.quiet_level)
    glob_match = GlobMatch(options.skip)

    bad_count = 0
    for filename in args:
        # ignore hidden files
        if is_hidden(filename, options.check_hidden):
            continue

        if os.path.isdir(filename):
            for root, dirs, files in os.walk(filename):
                if glob_match.match(root):  # skip (absolute) directories
                    del dirs[:]
                    continue
                for file_ in files:
                    if glob_match.match(file_):  # skip files
                        continue
                    fname = os.path.join(root, file_)
                    if glob_match.match(fname):  # skip paths
                        continue
                    if not os.path.isfile(fname) or not os.path.getsize(fname):
                        continue
                    bad_count += parse_file(
                        fname, colors, summary, misspellings, exclude_lines,
                        file_opener, word_regex, context, options)

                # skip (relative) directories
                dirs[:] = [dir_ for dir_ in dirs if not glob_match.match(dir_)]

        else:
            bad_count += parse_file(
                filename, colors, summary, misspellings, exclude_lines,
                file_opener, word_regex, context, options)

    if summary:
        print("\n-------8<-------\nSUMMARY:")
        print(summary)
    return bad_count
