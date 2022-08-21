#!/usr/bin/env python
from argparse import (
    FileType,
    SUPPRESS,
    _HelpAction,
    _SubParsersAction,
    _VersionAction,
)
import os
from os.path import dirname as dirn
import sys
from typing import Final, Tuple

from setuptools import find_packages

rootpath = dirn(dirn(os.path.abspath(__file__)))
path = os.path.join(rootpath, "src")
packages = find_packages(path)
if packages == []:
    path = rootpath
    packages = find_packages(path)
sys.path.insert(0, path)
PACKAGES: Final = packages
PACKAGE: Final = PACKAGES[0] if sys.argv[1:2] == [] else sys.argv[1]
_, parser = __import__(PACKAGE).parse_options({})
actions = parser._actions
BINNAME: Final = "codespell"
BINNAMES: Final = [BINNAME]
ZSH_COMPLETION_FILE: Final = (
    "_" + BINNAME if sys.argv[2:3] == [] else sys.argv[2]
)
ZSH_COMPLETION_TEMPLATE: Final = os.path.join(
    dirn(os.path.abspath(__file__)), "zsh_completion.in"
)
SUPPRESS_HELP = SUPPRESS
SUPPRESS_USAGE = SUPPRESS

flags = []
position = 1
for action in actions:
    if action.__class__ in [_HelpAction, _VersionAction]:
        prefix = "'(- *)'"
    elif isinstance(action, _SubParsersAction):  # TODO
        raise NotImplementedError
    else:
        prefix = ""

    if len(action.option_strings) > 1:  # {} cannot be quoted
        optionstr = "{" + ",".join(action.option_strings) + "}'"
    elif len(action.option_strings) == 1:
        optionstr = action.option_strings[0] + "'"
    else:  # action.option_strings == [], positional argument
        if action.nargs in ["*", "+"]:
            optionstr = "'*"  # * must be quoted
        else:
            if isinstance(action.nargs, int) and action.nargs > 1:
                old_position = position
                position += action.nargs
                optionstr = ",".join(map(str, range(old_position, position)))
                optionstr = "{" + optionstr + "}'"
            else:  # action.nargs in [1, None, "?"]:
                optionstr = str(position) + "'"
                position += 1

    if action.help not in [None, SUPPRESS] and action.option_strings != []:
        helpstr = action.help.replace("]", "\\]").replace("'", "'\\''")
        helpstr = "[" + helpstr + "]"
    else:
        helpstr = ""

    if isinstance(action.metavar, str):
        metavar = action.metavar
    elif isinstance(action.metavar, Tuple):
        metavar = " ".join(map(str, action.metavar))
        # need some changes in template file
    else:  # action.metavar is None
        if action.nargs == 0:
            metavar = ""
        elif action.option_strings == []:
            metavar = action.dest
        elif isinstance(action.type, FileType):
            metavar = "file"
        elif action.type:
            metavar = action.type.__name__
        else:
            metavar = action.default.__class__.__name__
    if metavar != "":
        # use lowcase conventionally
        metavar = metavar.lower().replace(":", "\\:")

    if action.choices:
        completion = "(" + " ".join(map(str, action.choices)) + ")"
    elif metavar == "file":
        completion = "_files"
        metavar = " "
    elif metavar == "dir":
        completion = "_dirs"
        metavar = " "
    elif metavar == "url":
        completion = "_urls"
        metavar = " "
    elif metavar == "command":
        completion = "_command_names -e"
        metavar = " "
    else:
        completion = ""

    if metavar != "":
        metavar = ":" + metavar
    if completion != "":
        completion = ":" + completion

    flag = "{0}{1}{2}{3}{4}'".format(
        prefix, optionstr, helpstr, metavar, completion
    )
    flags += [flag]

with open(ZSH_COMPLETION_TEMPLATE) as f:
    template = f.read()

template = template.replace("{{programs}}", " ".join(BINNAMES))
template = template.replace("{{flags}}", " \\\n  ".join(flags))

with (
    open(ZSH_COMPLETION_FILE, "w")
    if ZSH_COMPLETION_FILE != "-"
    else sys.stdout
) as f:
    f.write(template)
