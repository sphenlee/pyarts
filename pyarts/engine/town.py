'''
Town

A town is a group of entities sharing resources.
'''

from .resource import ResourcePool

class Town(object):
    def __init__(self, twid, team):
        self.twid = twid
        self.team = team
        self.eng = team.eng

        self.resources = ResourcePool(self)

        self.eids = set()
        self.towncomponents = set()

    def __repr__(self):
        return '<Town %d owned by %r>' % (self.twid, self.team)

    def load(self, data):
        self.race = self.eng.getrace(data['race'])
        self.resources.load(data['resources'])

    def save(self):
        return {
            'race' : self.race['name'],
            'resources' : self.resources.save()
        }

    def addentity(self, ent):
        print 'adding entity %d to town %r' % (ent.eid, self)
        self.eids.add(ent.eid)
        self.towncomponents.add(ent.town)

    def contains(self, pt):
        for tc in self.towncomponents:
            if tc.contains(pt):
                return True

        return False
