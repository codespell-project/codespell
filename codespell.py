#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
from optparse import OptionParser
import os

USAGE = """
\t%prog [OPTIONS] dict_filename [file1 file2 ... fileN]
"""
misspellings = {}
options = None

#OPTIONS:
#
#ARGUMENTS:
#    dict_filename       The file containing the dictionary of misspellings.
#                        If set to '-', it will be read from stdin
#    file1 .. fileN      Files to check spelling

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

# -.-:-.-:-.-:-.:-.-:-.-:-.-:-.-:-.:-.-:-.-:-.-:-.-:-.:-.-:-

def parse_options(args):
    parser = OptionParser(usage=USAGE)

    parser.add_option('-d', '--disable-colors',
                        action = 'store_true', default = False,
                        help = 'Disable colors even when printing to terminal')
    parser.add_option('-r', '-R',
                        action = 'store_true', default = False,
                        dest = 'recursive',
                        help = 'parse directories recursively')

    (options, args) = parser.parse_args()
    if (len(args) < 1):
        print('ERROR: you need to specify a dictionary!', file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    if (len(args) == 1):
        args.append('-')

    return options, args


def build_dict(filename):
    with open(filename, 'r') as f:
        for line in f:
            [key, data] = line.split('->')
            fix = data.find(',')

            if fix != (len(data) - 1) and fix > 0:
                reason = data.split(',')[-1].strip()
            else:
                reason = ''

            if fix > 0:
                fix = True
                data = "%s\n" % data[:data.rfind(',')]

            misspellings[key] = Mispell(data, fix, reason)

def istextfile(filename):
    with open(filename, mode='rb') as f:
        s = f.read(1024)
        if 0 in s:
            return False

        return True

def parse_file(filename, colors):
    if filename == '-':
        f = sys.stdin
    else:
        # ignore binary files
        if not istextfile(filename):
            print("Ignoring binary file: %s " % filename, file=sys.stderr)
            return

        f = open(filename, 'r')

    i = 1
    try:
        for line in f:
            for word in re.findall('\w+', line):
                if word in misspellings:
                    cfilename = "%s%s%s" % (colors.FILE, filename, colors.DISABLE)
                    cline = "%s%d%s" % (colors.FILE, i, colors.DISABLE)
                    cwrongword = "%s%s%s" % (colors.WWORD, word, colors.DISABLE)
                    crightword = "%s%s%s" % (colors.FWORD,
                                                misspellings[word].data.strip(),
                                                colors.DISABLE)
                    if misspellings[word].reason:
                        creason = "  | %s%s%s\n" % (colors.FILE,
                                                misspellings[word].reason,
                                                colors.DISABLE)
                    else:
                        creason = '\n'

                    if f != sys.stdin:
                        print("%(FILENAME)s:%(LINE)s: %(WRONGWORD)s "       \
                                " ==> %(RIGHTWORD)s%(REASON)s"
                                % {'FILENAME': cfilename, 'LINE': cline,
                                   'WRONGWORD': cwrongword,
                                   'RIGHTWORD': crightword, 'REASON': creason },
                                end='')
                    else:
                        print('%(LINE)s: %(STRLINE)s\n\t%(WRONGWORD)s ' \
                                '==> %(RIGHTWORD)s%(REASON)s'
                                % { 'LINE': cline, 'STRLINE': line.strip(),
                                    'WRONGWORD': cwrongword,
                                   'RIGHTWORD': crightword, 'REASON': creason },
                                end='')
            i += 1
    except UnicodeDecodeError:
            # just print a warning
            print('Error decoding file: %s' % filename, file=sys.stderr)

    if f != sys.stdin:
        f.close()


def main(*args):
    (options, args) = parse_options(args)

    build_dict(args[0])
    colors = TermColors();
    if options.disable_colors:
        colors.disable()

    for filename in args[1:]:
        # ignore hidden files
        bfilename = os.path.basename(filename)
        if bfilename != '' and bfilename != '.' and bfilename != '..' \
                                                 and bfilename[0] == '.':
            continue

        if not options.recursive and os.path.isdir(filename):
            continue

        if os.path.isdir(filename):
            for root, dirs, files in os.walk(filename):
                for file in files:
                    parse_file(os.path.join(root, file), colors)

            continue

        parse_file(filename, colors)

if __name__ == '__main__':
    sys.exit(main(*sys.argv))
