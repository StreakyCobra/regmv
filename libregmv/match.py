# -*- coding: utf-8 -*-

import os
import re
from libregmv.messages import Message

msg = Message()


def match(listing, reMatch, reReplace, path=False):
    if path:
        msg.debug('Chose path matching')
        return match_path(listing, reMatch, reReplace)
    else:
        msg.debug('Chose name matching')
        return match_name(listing, reMatch, reReplace)


def match_name(listing, reMatch, reReplace):
    # For each element in the listing
    for (root, filename) in listing:

        # Keep old path
        current = os.path.join(root, filename)

        msg.debug('Starting to match regex on name: %s' % current)

        # Try to substitute the regular expression on filename
        newname = re.sub(reMatch, reReplace, filename)

        # If there is no change skip (either bad match or no change)
        if filename == newname:
            msg.trace('No matching regexp on name: %s' % current)
            continue

        msg.trace('Matching regexp on name: %s -> %s' % (filename, newname))

        # Otherwise yield the change
        msg.trace('Yield a result matching the regexp on name: %s' % current)
        yield (os.path.join(root, filename), os.path.join(root, newname))


def match_path(listing, reMatch, reReplace):
    # For each element in the listing
    for (root, filename) in listing:

        # Save current path
        current = os.path.join(root, filename)

        msg.debug('Starting to match regex on path: %s' % current)

        # Try to substitute the regular expression on path
        newpath = re.sub(reMatch, reReplace, current)

        # If there is no change skip (either bad match or no change)
        if current == newpath:
            msg.trace('No matching regexp on path: %s' % current)
            continue

        msg.trace('Matching regexp on path: %s -> %s' % (current, newpath))

        # Otherwise yield the change
        msg.trace('Yield a result matching the regexp on path: %s' % current)
        yield(current, newpath)