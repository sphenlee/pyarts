'''
Steering

Component to move an entity using a velocity
'''

from __future__ import division

from math import sqrt
from .component import Component, register

@register
class Steering(Component):
    depends = ['locator', 'stats']

    def inject(self, locator, stats):
        self.locator = locator
        self.stats = stats

        self.dx = 0
        self.dy = 0

    def configure(self, data):
        pass

    def save(self):
        return {}

    def load(self, data):
        pass

    def stop(self):
        self.dx = 0
        self.dy = 0

    def towards(self, pos):
        cur = self.locator.pos()

        dx, dy = pos[0] - cur[0], pos[1] - cur[1]
        s = sqrt(dx*dx + dy*dy) / self.stats.get('speed', 8)

        if s:
            self.dx = int(dx / s)
            self.dy = int(dy / s)
        else:
            self.stop()

    def step(self):
        if self.dx or self.dy:
            self.locator.move(
                self.locator.x + self.dx,
                self.locator.y + self.dy)
