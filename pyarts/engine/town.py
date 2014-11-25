'''
Town

A town is a group of entities sharing resources.
'''

from .resource import ResourcePool

class Town(object):
    def __init__(self, twid, team):
        self.twid = twid
        self.team = team

        self.resources = ResourcePool()

        self.eids = set()
        self.towncomponents = set()

    def load(self, data):
        pass

    def save(self):
        return { }

    def addentity(self, ent):
        print 'adding entity %d to town %d' % (ent.eid, self.twid)
        self.eids.add(ent.eid)
        self.towncomponents.add(ent.town)

    def contains(self, pt):
        for tc in self.towncomponents:
            if tc.contains(pt):
                return True

        return False
