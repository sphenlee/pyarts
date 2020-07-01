'''
Town

Component for entities that must be in a town and
create 'town influence'
'''

from .component import Component, register

from ..pathfinder import distance

from pyarts.log import error, trace


@register
class Town(Component):
    depends = ['locator', '@team']

    def inject(self, locator, team):
        self.locator = locator
        self.locator.onplace.add(self.updateplace)
        self.team = team

    def configure(self, data):
        self.r2 = data['r'] ** 2

    def load(self, data):
        if 'id' in data:
            self.town = self.team.gettown(data['id'])
            trace('entity {} loading, adding itself to town {}', self.ent, self.town)
            self.town.addentity(self.ent)

    def updateplace(self, locator):
        self.town = self.team.gettownat(locator.pos())
        trace('{} has moved place, new town is {}', self, self.town)
        if self.town:
            self.town.addentity(self.ent)

    def save(self):
        return {
            'id': self.town.twid
        }

    def contains(self, pt):
        d = distance(pt, self.locator.pos())
        trace('contains: {} in {}@{}?', pt, self.locator.pos(), self.r2)
        trace('dist = {}', d)
        return d < self.r2

    def destroy(self):
        error('TODO - remove from town')
