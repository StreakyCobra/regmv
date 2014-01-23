# -*- coding: utf-8 -*-

import sys
from termcolor import colored
from libregmv.singleton import Singleton


# Message types
class MT:
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3
    SUCCESS = 4
    ERROR = 5
    DANGER = 6

    MT_NAME_MAXLEN = 11


@Singleton
class Message:
    def __init__(self, minlevel=MT.INFO, colored=True):
        # Register Message parameters
        self.minlevel = minlevel
        self.colored = colored

    def setMinlevel(self, val):
        self.minlevel = val

    def setColored(self, val):
        self.colored = val

    def _base(self, fg, bg=None):
        base = ''

        # Enable/Disable colors
        if self.colored:
            base += colored('%-' + str(MT.MT_NAME_MAXLEN) + 's ',
                            fg, bg, attrs=['bold'])
            base += colored('%s', fg, bg)
        else:
            base += '%-' + str(MT.MT_NAME_MAXLEN) + 's %s'

        # Base formatting
        return base

    def _formatting(self, level, text):
        if level == MT.TRACE:
            return self._base('magenta') % ('[ TRACE ]', text)
        if level == MT.DEBUG:
            return self._base('cyan') % ('[ DEBUG ]', text)
        if level == MT.INFO:
            return self._base('blue') % ('[ INFO ]', text)
        if level == MT.WARNING:
            return self._base('yellow') % ('[ WARNING ]', text)
        if level == MT.SUCCESS:
            return self._base('green') % ('[ SUCCESS ]', text)
        if level == MT.ERROR:
            return self._base('red') % ('[ ERROR ]', text)
        if level == MT.DANGER:
            return self._base('white', 'on_red') % ('[ DANGER ]', text)

    def message(self, level, text):
        # If below the min level, do nothing
        if level < self.minlevel:
            return

        # Message formating
        print(self._formatting(level, text),
              file=sys.stdout if level > MT.DEBUG else sys.stderr)

    def sep(self, char, fg='white', bg='on_grey'):
        if self.colored:
            print(colored(char * 80, fg, bg, attrs=['bold']))
        else:
            print(char * 80)

    def trace(self, text):
        self.message(MT.TRACE, text)

    def debug(self, text):
        self.message(MT.DEBUG, text)

    def info(self, text):
        self.message(MT.INFO, text)

    def warning(self, text):
        self.message(MT.WARNING, text)

    def success(self, text):
        self.message(MT.SUCCESS, text)

    def error(self, text):
        self.message(MT.ERROR, text)

    def danger(self, text):
        self.message(MT.DANGER, text)


if __name__ == "__main__":
    msg = Message(minlevel=MT.TRACE)
    msg.trace('Trace message')
    msg.debug('Debug message')
    msg.info('Info message')
    msg.warning('Warning message')
    msg.success('Success message')
    msg.error('Error message')
    msg.danger('Danger message')
    print('')
    msg = Message(minlevel=MT.TRACE, colored=False)
    msg.trace('Trace message')
    msg.debug('Debug message')
    msg.info('Info message')
    msg.warning('Warning message')
    msg.success('Success message')
    msg.error('Error message')
    msg.danger('Danger message')
