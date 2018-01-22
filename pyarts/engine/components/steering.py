'''
Steering

Component to move an entity using a velocity
'''

from __future__ import division

from math import sqrt, copysign
from .component import Component, register

def fromto(a, b):
    ''' vector from a to b '''
    return b[0] - a[0], b[1] - a[1]

def mag(a):
    ''' magnitude of a '''
    return sqrt(a[0]*a[0] + a[1]*a[1])

def normed(a, b):
    ''' normed vector from a to b '''
    d = fromto(a, b)
    m = mag(d)
    if m:
        return d[0]/m, d[1]/m
    else:
        return 0, 0

def dot(a, b):
    ''' dot product of a and b '''
    return a[0]*b[0] + a[1]*b[1]

@register
class Steering(Component):
    depends = ['locator', 'stats', '@map', '@collisions']

    def inject(self, locator, stats, map, collisions):
        self.locator = locator
        self.stats = stats
        self.map = map
        self.collisions = collisions

    def configure(self, data):
        self.dest = None

    def save(self):
        return {}

    def load(self, data):
        pass

    def stop(self):
        self.dest = None

    def towards(self, pos):
        self.dest = pos

    def step(self):
        if not self.dest:
            return

        cur = self.locator.pos()
        r = self.locator.r
        speed = self.stats.get('speed', 4)
        factor = 1

        # get normed vector of our direction
        d = normed(cur, self.dest)
        if d == (0, 0):
            return

        for hard, ent in self.collisions.getcollisions(self.eid):
            # get normed vector from us to them
            other = ent.locator.pos()
            e = normed(cur, other)
            if e == (0, 0):
                # we're at the same point, this breaks the formula below
                # and we want to allow these ents to move away from each other
                f = 1
            else:
                # get the slowdown factor
                f = max(min(1 - dot(d, e), 1), 0)

                if hard:
                    f = f * f

            # print '---collide ---'
            # print 'eid:', self.eid, 'to: ', ent.eid
            # print 'hard:', hard, 'f:', f
            # print '---'

            factor *= f



        # vector to target
        t = fromto(cur, self.dest)
        # range to target
        r = mag(t)
        if r == 0:
            return

        # desired speed
        s = min(r, speed) / r * factor

        # update final speeds
        dx = int(t[0] * s)
        dy = int(t[1] * s)

        # print '--- steering ---'
        # print 'eid:', self.eid
        # print 'cur:', cur, 'dest:', self.dest
        # print 'd:', d, 'target:', t, 'range:', r
        # print 'speed:', s, 'factor:', factor
        # print 'final:', (dx, dy)
        # print '---'

        if dx or dy:
            self.locator.move(
                self.locator.x + dx,
                self.locator.y + dy)
