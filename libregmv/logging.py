# -*- coding: utf-8 -*-

from libregmv.singleton import Singleton


@Singleton
class Logging:
    def __init__(self):
        self.log = []

    def add(self, cFrom, cTo):
        self.log.append((cFrom, cTo))

    def save(self, f):
        for (cFrom, cTo) in self.log:
            print('%s -> %s' % (cFrom, cTo), file=f)
