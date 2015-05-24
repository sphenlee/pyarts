'''
Steering

Component to move an entity using a velocity
'''

from __future__ import division

from math import sqrt
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

        for hard, ent in self.collisions.getcollisions(self.eid):
            other = ent.locator.pos()
            dx, dy = other[0] - cur[0], other[1] - cur[1]
            d = sqrt(dx*dx + dy*dy)

            s = -16.0 / d #-min(d, self.stats.get('speed', 4)) / d
            if not hard:
                s = s / 4.0

            fx += dx * s
            fy += dy * s

        if self.dest:
            dx, dy = self.dest[0] - cur[0], self.dest[1] - cur[1]
            d = sqrt(dx*dx + dy*dy)

            if d:
                s = min(d, self.stats.get('speed', 4)) / d
            
                fx += dx * s
                fy += dy * s

        self.dx = int(fx)
        self.dy = int(fy)
        print self.eid, fx, fy, self.dx, self.dy


        if self.dx or self.dy:
            self.locator.move(
                self.locator.x + self.dx,
                self.locator.y + self.dy)
