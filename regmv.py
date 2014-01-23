#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import collections
from libregmv.find import find
from libregmv.match import match
from libregmv.messages import Message, MT
from libregmv.logging import Logging

# Messaging and logging
msg = Message()
log = Logging()


def parser():
    """ Define the parser and parse arguments """
    # General parser
    parser = argparse.ArgumentParser(description='Move or rename files '
                                                 'using regular expressions',
                                     add_help=False)

    # Find group
    findGroup = parser.add_argument_group(title='Files selection',
                                          description='Options changing the '
                                          'way files are being selected')

    # -a option
    findGroup.add_argument('-a',
                           '--all',
                           action="store_true",
                           help='also move/rename hidden files (and recurse '
                           'in hidden directories if recursive flag is set)')

    # -R option
    findGroup.add_argument('-r',
                           '--recursive',
                           action="store_true",
                           help='move/rename file recursively')
    # -s option
    findGroup.add_argument('-s',
                           '--symlinks',
                           action="store_true",
                           help='follow symbolic links during recursion '
                           '(can lead into infinite recursion)')

    # -d option
    findGroup.add_argument('-d',
                           '--directories',
                           action="store_true",
                           help='work on directories instead of files')

    # Match group
    matchGroup = parser.add_argument_group(title='Pattern matching',
                                           description='Options changing the '
                                           'way pattern matching is applied')

    # -p option
    matchGroup.add_argument('-p',
                            '--path',
                            action="store_true",
                            help='Match the complete path instead of just the '
                            'basename. The paths are begining with \'./\'')

    # Danger group
    dangerGroup = parser.add_argument_group(title='Dangerous options',
                                            description='Options having '
                                            'effects on you filesystem')

    # -E option
    dangerGroup.add_argument('-E',
                             '--execute',
                             action="store_true",
                             help='CAUTION! Really EXECUTE the changes')

    # -B option
    dangerGroup.add_argument('-B',
                             '--bypass',
                             action="store_true",
                             help='CAUTION! Bypass the check function, can '
                             'cause IRREVERSIBLE dammages')

    # Disp group
    dispGroup = parser.add_argument_group(title='Display options',
                                          description='Options having '
                                          'effects program output')

    # -v option
    dispGroup.add_argument('-v',
                           metavar='VERBOSITY',
                           default=2,
                           type=int,
                           help='set the verbosity level (see man page)')

    # --no-color option
    dispGroup.add_argument('--no-color',
                           action="store_true",
                           help='disable colored output')

    dispGroup.add_argument('-h',
                           '--help',
                           action="help",
                           help="show this help message and exit")

    # MATCH argument
    parser.add_argument('MATCH',
                        help='regular expression to be matched')

    # REPLACE argument
    parser.add_argument('REPLACE',
                        help='regular expression to use as replacement')

    # Parse argument and return the result
    return parser.parse_args()


def check(changes, bypass=False):
    # If the bypass is not set
    if not bypass:

        # Get the sets
        msg.trace('Create sets to find duplicates')
        tos = [f for (_, f) in changes]
        listed = [os.path.realpath(f) for f in tos]
        unique = set(listed)

        msg.debug('Check for duplicate in ending paths')
        if len(listed) != len(unique):
            msg.error('Several files will end-up with the same path:')

            msg.trace('Prepare the list of duplicates')
            ends = [x for x, y in collections.Counter(tos).items() if y > 1]

            # Print list of duplicates
            msg.sep('=', fg='red', bg=None)
            [print("%s -> %s" % (a, b))
             for b in ends
             for (a, _) in changes if (a, b) in changes]
            msg.sep('=', fg='red', bg=None)

            sys.exit(1)

        msg.debug('Check for already existing paths')
        for (cFrom, cTo) in changes:
            if os.path.exists(cTo):
                msg.error('The following path already exist in filesystem:')
                msg.sep('=', fg='red', bg=None)
                print('%s -> %s' % (cFrom, cTo))
                msg.sep('=', fg='red', bg=None)
                sys.exit(1)
    else:
        msg.warning('Skip checkings')


def displayChanges(changes):
    msg.sep('-', fg='blue', bg=None)

    # Print the changes
    for cFrom, cTo in changes:
        print("%s -> %s" % (cFrom, cTo))

    msg.sep('-', fg='blue', bg=None)


def regmv(changes, execute=False, bypassed=False):
    # Ask confirmation if bypassed
    if execute and bypassed:
        msg.danger('Using flag \'-B\' can result in a loss of informations')
        resp = input(msg._formatting(MT.DANGER,
                                     'Continue anyway [y/N]')).lower()
        if resp != 'y' and resp != 'Y':
            msg.info('Aborting')
            exit(1)

    # If the action is wanted
    if execute:
        msg.debug('Execute mode')
        # For each change:
        for cFrom, cTo in changes:
            msg.debug('Treating: %s -> %s' % (cFrom, cTo))

            # Get the new path
            path = os.path.dirname(cTo)

            # Ensure the path is existing
            msg.trace('Check for existence of path to: %s' % path)
            if not os.path.isdir(path):
                msg.trace('Create path: %s' % path)
                os.makedirs(path, exist_ok=True)

            msg.trace('Check for existence of path: %s' % cTo)
            if not bypassed and os.path.exists(cTo):
                msg.error('Ahem, the file %s already exist. This normally '
                          'must not append without the \'-B\' flag. Saving '
                          'the log into "REGMV.LOG" and exiting' % cTo)
                emergencyExit()

            msg.debug('Renaming: %s -> %s' % (cFrom, cTo))
            log.add(cFrom, cTo)
            os.rename(cFrom, cTo)

        msg.success('All changes seems to be executed correctly')
    else:
        msg.debug('Not execute mode')
        msg.success('The listed changes seems to be OK for execution')
        msg.success('If you agree, pass argument \'-E\' to execute them')

        if bypassed:
            msg.danger('Using flag \'-B\' can result in a loss '
                       'of informations')


def emergencyExit():
    log.save(open('REGMV.LOG', 'a'))
    sys.exit(1)


def main():
    # Parse arguments
    args = parser()

    # Init messaging system
    msg.setMinlevel(args.v)
    msg.setColored((not args.no_color) & sys.stdout.isatty())

    # Find files and directories that must be used
    msg.info('Find all files/directories matching given flags')
    listing = list(find(recurse=args.recursive,
                        hidden=args.all,
                        symlinks=args.symlinks,
                        includeFiles=not args.directories,
                        includeDirs=args.directories))
    # Look in the list for matching regex
    msg.info('Filter files/directories matching the regular expression')
    changes = list(match(listing,
                         args.MATCH,
                         args.REPLACE,
                         path=args.path))

    # Verify there is changes before continuing
    if not len(changes):
        msg.warning('There is no changes')
        sys.exit(0)

    # Check resulting file paths to avoid conflicts
    msg.info('Check final paths for files/directories conflicts')
    check(changes,
          args.bypass)

    # Print the changes
    msg.info('Display the changes')
    displayChanges(changes)

    # Do an action with the changes
    msg.info('Analyze and/or apply the changes')
    regmv(changes,
          execute=args.execute,
          bypassed=args.bypass)


if __name__ == "__main__":
    main()
