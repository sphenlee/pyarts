'''
Town

A town is a group of entities sharing resources.
'''

from pyarts.container import dynamic_component

from .resource import ResourcePool
from .event import Event

from pyarts.log import debug, warn


@dynamic_component
class Town(object):
    depends = ['engine', 'entitymanager']

    def __init__(self, twid, team):
        self.twid = twid
        self.name = None
        self.team = team
        self.resources = ResourcePool(self)

        self.eids = set()
        self.towncomponents = set()
        self.founder_eid = None

        self.onentityadded = Event(debug='onentityadded')

    def inject(self, engine, entitymanager):
        self.eng = engine
        self.em = entitymanager

    def __repr__(self):
        return '<Town %d "%s" owned by %r>' % (self.twid, self.name, self.team)

    def load(self, data):
        self.name = data.get('name', '')
        self.race = self.eng.getrace(data['race'])
        self.resources.load(data['resources'])
        self.founder_eid = data['founder']
        # TODO - how do we ensure the founder is always added to the town?

    def save(self):
        return {
            'name': self.name,
            'race': self.race['name'],
            'resources': self.resources.save(),
            'founder': self.founder_eid
        }

    @property
    def founder(self):
        try:
            return self.em.get(self.founder_eid)
        except  KeyError:
            debug('founder not loaded yet {} {}', self, self.founder_eid)
            return None

    def addentity(self, ent):
        debug('adding entity {} to town {}', ent.eid, self)
        self.eids.add(ent.eid)
        self.towncomponents.add(ent.town)

        self.onentityadded.emit(self, ent)

    def contains(self, pt):
        for tc in self.towncomponents:
            if tc.contains(pt):
                return True

        return False
