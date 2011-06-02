#!/usr/bin/env python3
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

import sys
import re
from optparse import OptionParser
import os

USAGE = """
\t%prog [OPTIONS] dict_filename [file1 file2 ... fileN]
"""
VERSION = '1.1-rc1'

misspellings = {}
exclude_lines = set()
options = None
quiet_level = 0
encodings = [ 'utf-8', 'iso-8859-1' ]

#OPTIONS:
#
#ARGUMENTS:
#    dict_filename       The file containing the dictionary of misspellings.
#                        If set to '-', it will be read from stdin
#    file1 .. fileN      Files to check spelling

class QuietLevels:
    NONE = 0
    ENCODING = 1
    BINARY_FILE = 2
    DISABLED_FIXES = 4
    NON_AUTOMATIC_FIXES = 8
    FIXES = 16


class Mispell:
    def __init__(self, data, fix, reason):
        self.data = data
        self.fix = fix
        self.reason = reason

class TermColors:
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

class Summary:
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

        return "\n".join(["{0}{1:{width}}".format(key, self.summary.get(key), width=15 - len(key)) for key in keys])

# -.-:-.-:-.-:-.:-.-:-.-:-.-:-.-:-.:-.-:-.-:-.-:-.-:-.:-.-:-

def parse_options(args):
    parser = OptionParser(usage=USAGE, version=VERSION)

    parser.add_option('-d', '--disable-colors',
                        action = 'store_true', default = False,
                        help = 'Disable colors even when printing to terminal')
    parser.add_option('-r', '-R',
                        action = 'store_true', default = False,
                        dest = 'recursive',
                        help = 'parse directories recursively')
    parser.add_option('-w', '--write-changes',
                        action = 'store_true', default = False,
                        help = 'write changes in place if possible')

    parser.add_option('-s', '--summary',
                        action = 'store_true', default = False,
                        help = 'print summary of fixes')

    parser.add_option('-x', '--exclude-file',
                        help = 'FILE with lines that should not be changed',
                        metavar='FILE')

    parser.add_option('-i', '--interactive',
                        action='store', type='int', default=0,
                        help = 'Set interactive mode when writing changes. '  \
                                '0 is the same of no interactivity; 1 makes ' \
                                'codespell ask confirmation; 2 ask user to '  \
                                'choose one fix when more than one is ' \
                                'available; 3 applies both 1 and 2')

    parser.add_option('-q', '--quiet-level',
                        action='store', type='int', default=0,
                        help = 'Bitmask that allows codespell to run quietly.'\
                                '0: the default, in which all messages are '\
                                'printed. 1: disable warnings about wrong '\
                                'encoding. 2: disable warnings about binary'\
                                ' file. 4: shut down warnings about automatic'\
                                ' fixes that were disabled in dictionary. '\
                                '8: don\'t print anything for non-automatic '\
                                'fixes. 16: don\'t print fixed files.')


    (o, args) = parser.parse_args()
    if (len(args) < 1):
        print('ERROR: you need to specify a dictionary!', file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    if (len(args) == 1):
        args.append('-')

    return o, args

def build_exclude_hashes(filename):
    with open(filename, 'r') as f:
        for line in f:
            exclude_lines.add(line)

def build_dict(filename):
    with open(filename, 'r') as f:
        for line in f:
            [key, data] = line.split('->')
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

            misspellings[key] = Mispell(data, fix, reason)

def ishidden(filename):
    bfilename = os.path.basename(filename)

    if bfilename != '' and bfilename != '.' and bfilename != '..' \
                                                 and bfilename[0] == '.':
        return True

    return False


def istextfile(filename):
    with open(filename, mode='rb') as f:
        s = f.read(1024)
        if 0 in s:
            return False

        return True

def ask_for_word_fix(line, wrongword, misspelling, interactivity):
    if interactivity <= 0:
        return misspelling.fix, misspelling.data

    if misspelling.fix and interactivity & 1:
        r = ''
        while not r:
            print("%s\t%s  ==> %s (Y/n) " %  (line, wrongword,
                                                misspelling.data), end='')
            r = sys.stdin.readline().strip().upper()
            if not r: r = 'Y'
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
                print(" %d) %s" % (i, opt[i]), end='')
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

    return misspelling.fix, misspelling.data

def parse_file(filename, colors, summary):
    lines = None
    changed = False
    global misspellings
    global options
    global encodings
    global quiet_level

    encoding = encodings[0]  # if not defined, use UTF-8

    if filename == '-':
        f = sys.stdin
        lines = f.readlines()
    else:
        # ignore binary files
        if not istextfile(filename):
            if not quiet_level & QuietLevels.BINARY_FILE:
                print("WARNING: Binary file: %s " % filename, file=sys.stderr)
            return

        curr = 0
        while True:
            try:
                f = open(filename, 'r', encoding=encodings[curr])
                lines = f.readlines()
                break
            except UnicodeDecodeError:

                if not quiet_level & QuietLevels.ENCODING:
                    print('WARNING: Decoding file %s' % filename,
                                                            file=sys.stderr)
                    print('WARNING: using encoding=%s failed. '
                                                            % encodings[curr],
                                                            file=sys.stderr)
                    print('WARNING: Trying next encoding: %s' % encodings[curr],
                                                            file=sys.stderr)

                curr += 1

            finally:
                f.close()

        if not lines:
            print('ERROR: Could not detect encoding: %s' % filename,
                                                            file=sys.stderr)
            return

        encoding = encodings[curr]

    i = 1
    rx = re.compile(r"[\w']+")
    for line in lines:
        if line in exclude_lines:
            i += 1
            continue

        for word in rx.findall(line):
            lword = word.lower()
            if lword in misspellings:
                fix = misspellings[lword].fix

                if word == word.capitalize():
                    fixword = misspellings[lword].data.capitalize()
                elif word == word.upper():
                    fixword = misspellings[lword].data.upper()
                else:
                    # even they are the same lower case or
                    # or we don't have any idea
                    fixword = misspellings[lword].data

                if options.interactive:
                    fix, fixword = ask_for_word_fix(lines[i - 1], word,
                                                    misspellings[lword],
                                                    options.interactive)

                if summary and fix:
                    summary.update(lword)

                if options.write_changes and fix:
                    changed = True
                    lines[i - 1] = lines[i - 1].replace(word, fixword, 1)
                    continue

                # otherwise warning was explicitly set by interactive mode
                if options.interactive & 2 and not fix and not misspellings[lword].reason:
                    continue

                cfilename = "%s%s%s" % (colors.FILE, filename, colors.DISABLE)
                cline = "%s%d%s" % (colors.FILE, i, colors.DISABLE)
                cwrongword = "%s%s%s" % (colors.WWORD, word, colors.DISABLE)
                crightword = "%s%s%s" % (colors.FWORD, fixword, colors.DISABLE)

                if misspellings[lword].reason:
                    if quiet_level & QuietLevels.DISABLED_FIXES:
                        continue

                    creason = "  | %s%s%s" % (colors.FILE,
                                            misspellings[lword].reason,
                                            colors.DISABLE)
                else:
                    if quiet_level & QuietLevels.NON_AUTOMATIC_FIXES:
                        continue

                    creason = ''

                if filename != '-':
                    print("%(FILENAME)s:%(LINE)s: %(WRONGWORD)s "       \
                            " ==> %(RIGHTWORD)s%(REASON)s"
                            % {'FILENAME': cfilename, 'LINE': cline,
                               'WRONGWORD': cwrongword,
                               'RIGHTWORD': crightword, 'REASON': creason })
                else:
                    print('%(LINE)s: %(STRLINE)s\n\t%(WRONGWORD)s ' \
                            '==> %(RIGHTWORD)s%(REASON)s'
                            % { 'LINE': cline, 'STRLINE': line.strip(),
                                'WRONGWORD': cwrongword,
                               'RIGHTWORD': crightword, 'REASON': creason })
        i += 1

    if changed:
        if filename == '-':
            print("---")
            for line in lines:
                print(line, end='')
        else:
            if not quiet_level & QuietLevels.FIXES:
                print("%sFIXED:%s %s" % (colors.FWORD, colors.DISABLE, filename),
                                                                file=sys.stderr)
            f = open(filename, 'w', encoding=encoding)
            f.writelines(lines)
            f.close()


def main(*args):
    global options
    global quiet_level

    (options, args) = parse_options(args)

    build_dict(args[0])
    colors = TermColors();
    if options.disable_colors:
        colors.disable()

    if options.summary:
        summary = Summary()
    else:
        summary = None

    if options.exclude_file:
        build_exclude_hashes(options.exclude_file)

    if options.quiet_level:
        quiet_level = options.quiet_level

    for filename in args[1:]:
        # ignore hidden files
        if ishidden(filename):
            continue

        if not options.recursive and os.path.isdir(filename):
            continue

        if os.path.isdir(filename):
            for root, dirs, files in os.walk(filename):
                i = 0
                for d in dirs:
                    if ishidden(d):
                        del dirs[i]
                    else:
                        i += 1

                for file in files:
                    if os.path.islink(file):
                        continue

                    parse_file(os.path.join(root, file), colors, summary)

            continue

        parse_file(filename, colors, summary)

    if summary:
        print("\n-------8<-------\nSUMMARY:")
        print(summary)

if __name__ == '__main__':
    sys.exit(main(*sys.argv))
