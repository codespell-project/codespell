#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2010 Lucas De Marchi <lucas.de.marchi@gmail.com>
"""

import sys
import re
from optparse import OptionParser
import os

USAGE = """
\t%prog [OPTIONS] dict_filename [file1 file2 ... fileN]
"""
VERSION = '0.9'

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

    (o, args) = parser.parse_args()
    if (len(args) < 1):
        print('ERROR: you need to specify a dictionary!', file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    if (len(args) == 1):
        args.append('-')

    return o, args


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
                data = data[:fix]
                reason = data[fix + 1:].strip()
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

def parse_file(filename, colors):
    lines = None
    changed = False
    global misspellings
    global options

    if filename == '-':
        f = sys.stdin
    else:
        # ignore binary files
        if not istextfile(filename):
            print("Ignoring binary file: %s " % filename, file=sys.stderr)
            return

        f = open(filename, 'r')

    try:
        lines = f.readlines()
    except UnicodeDecodeError:
            # just print a warning
            print('Error decoding file: %s' % filename, file=sys.stderr)
            return
    finally:
        if filename == '-':
            f.close()

    i = 1
    for line in lines:
        for word in re.findall('\w+', line):
            lword = word.lower()
            if lword in misspellings:
                if options.write_changes and misspellings[lword].fix:
                    changed = True
                    lines[i - 1] = line.replace(word.capitalize(),
                                        misspellings[lword].data.capitalize())
                    lines[i - 1] = lines[i - 1].replace(word.upper(),
                                        misspellings[lword].data.upper())
                    lines[i - 1] = lines[i - 1].replace(word,
                                                       misspellings[lword].data)

                    continue

                cfilename = "%s%s%s" % (colors.FILE, filename, colors.DISABLE)
                cline = "%s%d%s" % (colors.FILE, i, colors.DISABLE)
                cwrongword = "%s%s%s" % (colors.WWORD, word, colors.DISABLE)
                crightword = "%s%s%s" % (colors.FWORD,
                                            misspellings[lword].data,
                                            colors.DISABLE)
                if misspellings[lword].reason:
                    creason = "  | %s%s%s" % (colors.FILE,
                                            misspellings[lword].reason,
                                            colors.DISABLE)
                else:
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
            print("%sFIXED:%s %s" % (colors.FWORD, colors.DISABLE, filename),
                                    file=sys.stderr)
            f = open(filename, 'w')
            f.writelines(lines)
            f.close()


def main(*args):
    global options
    (options, args) = parse_options(args)

    build_dict(args[0])
    colors = TermColors();
    if options.disable_colors:
        colors.disable()

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
                    parse_file(os.path.join(root, file), colors)

            continue

        parse_file(filename, colors)

if __name__ == '__main__':
    sys.exit(main(*sys.argv))
