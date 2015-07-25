'''
Steering

Component to move an entity using a velocity
'''

from __future__ import division

from math import sqrt, exp
from .component import Component, register

@register
class Steering(Component):
    depends = ['locator', 'stats', '@map', '@collisions']

    def inject(self, locator, stats, map, collisions):
        self.locator = locator
        self.stats = stats
        self.map = map
        self.collisions = collisions

    def configure(self, data):
        self.dx = 0
        self.dy = 0
        self.dest = None

    def save(self):
        return {}

    def load(self, data):
        pass

    def stop(self):
        self.dx = 0
        self.dy = 0
        self.dest = None

    def towards(self, pos):
        self.dest = pos

    def step(self):
        fx, fy = 0.0, 0.0
        cur = self.locator.pos()
        r = self.locator.r
        speed = self.stats.get('speed', 4)

        collision = False
        for hard, ent in self.collisions.getcollisions(self.eid):
            collision = True
            other = ent.locator.pos()
            dx, dy = other[0] - cur[0], other[1] - cur[1]
            d = sqrt(dx*dx + dy*dy)

            #if hard:
            s = -r * exp(-d/r)# * 8
            print self.eid, 'rds', r, d, s
            print self.eid, 'dxdy', dx, dy
            #    #/ d #-min(d, self.stats.get('speed', 4)) / d
            #else:
            #    s = -4.0 / d

            if dx == 0 and dy == 0:
                dx += 0.1 * (1 if self.eid % 2 else -1)

            fx += dx * s
            fy += dy * s

            print self.eid, 'col', ent.eid, fx, fy, d

        if self.dest:
            dx, dy = self.dest[0] - cur[0], self.dest[1] - cur[1]
            d = sqrt(dx*dx + dy*dy)

            if d:
                s = min(d, speed) / d
            
                fx += dx * s
                fy += dy * s

        d = sqrt(fx*fx + fy*fy)
        print self.eid, 'f', fx, fy, d
        if d:
            s = min(d, speed) / d

            self.dx = int(fx * s)
            self.dy = int(fy * s)
            print self.eid, 'fd', fx, fy, self.dx, self.dy
        else:
            self.dx = 0
            self.dy = 0


        if self.dx or self.dy:
            self.locator.move(
                self.locator.x + self.dx,
                self.locator.y + self.dy)
