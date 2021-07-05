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
            self.twid = data['id']
            trace('entity {} loading, adding itself to town {}', self.ent, self.twid)
            #self.town.addentity(self.ent)

    @property
    def town(self):
        return self.team.gettown(self.twid)
    

    def updateplace(self, locator):
        town = self.team.gettownat(locator.pos())
        trace('{} has moved place, new town is {}', self, town)
        if town:
            self.twid = town.twid
            town.addentity(self.ent)

    def save(self):
        return {
            'id': self.twid
        }

    def contains(self, pt):
        d = distance(pt, self.locator.pos())
        trace('contains: {} in {}@{}?', pt, self.locator.pos(), self.r2)
        trace('dist = {}', d)
        return d < self.r2

    def destroy(self):
        error('TODO - remove from town')
