# -*- coding: utf-8 -*-

import os
from libregmv.messages import Message

msg = Message()


def find(recurse=False, **kwargs):
    if recurse:
        msg.debug('Chose recursive find')
        return find_r(**kwargs)
    else:
        msg.debug('Chose non-recursive find')
        return find_nr(**kwargs)


def find_nr(hidden=False, symlinks=False,
            includeFiles=True, includeDirs=False):

    # List files and folders of the current directory
    files = [f for f in os.listdir('./')]
    msg.debug('List the current directory only')

    # Remove hidden files an folders if specified
    if not hidden:
        msg.debug('Removing hidden elements from the results')
        files = [f for f in files if not f[0] == '.']

    # Use dirs if specified
    if not includeDirs:
        msg.debug('Removing directories from the results')
        files = filter(lambda x: not os.path.isdir(x), files)

    # Use dirs if specified
    if not includeFiles:
        msg.debug('Removing files from the results')
        files = filter(lambda x: not os.path.isfile(x), files)

    # Return the result
    for f in files:
        msg.trace('Yield an element from the results: ./%s' % f)
        yield ('./', f)


def find_r(hidden=False, symlinks=False,
           includeFiles=True, includeDirs=False):

    # Walk recursively through the current directory
    for root, dirs, files in os.walk('./', followlinks=symlinks):
        msg.debug('List the following directory recursively: %s' % root)

        # Remove hidden files an folders if specified
        if not hidden:
            msg.debug('Removing hidden elements from the results')
            dirs[:] = [d for d in dirs if not d[0] == '.']
            files = [f for f in files if not f[0] == '.']

        # Use dirs if specified
        if includeDirs:
            msg.debug('Inculding directories in the results')
            for dirname in dirs:
                msg.trace('Yield a directory from the results: %s, %s' %
                          (root, dirname))
                yield (root, dirname)

        # Use files if specified
        if includeFiles:
            msg.debug('Inculding files in the results')
            for filename in files:
                msg.trace('Yield a file from the results: %s, %s' %
                          (root, filename))
                yield (root, filename)
