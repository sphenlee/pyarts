'''
Town

Component for entities that must be in a town and
create 'town influence'
'''

from .component import Component, register

from ..pathfinder import distance

@register
class Town(Component):
    depends = ['locator', '@team']

    def inject(self, locator, team):
        self.locator = locator
        self.team = team

    def configure(self, data):
        self.r2 = data['r'] ** 2

    def load(self, data):
        if data is not None:
            self.town = self.team.gettown(int(data))
        else:
            # new entity, search for the right town
            # founding a town requires that an empty town is created first
            self.town = self.team.gettownat(self.locator.pos())

        self.town.addentity(self.ent)

    def save(self):
        return self.town.twid

    def contains(self, pt):
        return distance(pt, self.locator.pos()) < self.r2

    def destroy(self):
        print('TODO - remove from town')
