'''
EntityManager

Container holding all of the entities
'''

from .components.component import getcomponentclass
from .entity import Entity
from pyarts.game.order import Order
from .actions import AbilityAction
from .event import Event

from pyarts.container import component

@component
class EntityManager(object):
    depends = ['engine', 'datasrc', 'map']

    def __init__(self):
        self.nextentid = 0
        self.entities = {} # entid -> entitiy
        self.newentities = {} # entities created during this step

        self.onentitycreated = Event()

    def inject(self, engine, datasrc, map):
        self.eng = engine
        self.datasrc = datasrc
        self.map = map

    def get(self, eid):
        ''' Get an entity by ID '''
        try:
            return self.entities[eid]
        except KeyError:
            return self.newentities[eid]

    def load(self):
        ''' Individual entities are loaded as the map loads sectors, juts grab misc data here '''
        self.nextentid = self.datasrc.getmisc('entities.nexteid', 1)

        self.map.onsectorloaded.add(self.sectorloaded)


    def loadentity(self, eid):
        ''' Load a single entity by eid '''
        data = self.datasrc.getentity(eid)
        team = self.eng.getteam(data['team'])
        proto = team.getproto(data['proto'])
        ent = self._docreate(proto, eid=int(eid))
        ent.load(data)

    def create(self, proto, eid=None):
        '''Create an entity from a proto and load it with no data (to indicate that it is freshly created)'''
        ent = self._docreate(proto, eid)
        ent.load({})
        return ent

    def save(self, sink):
        ''' Save all the entities '''
        for eid, ent in self.entities.iteritems():
            data = ent.save()
            sink.addentity(eid, data)

        sink.setmisc('entities.nextentid', self.nextentid)

    def _docreate(self, proto, eid=None):
        '''Create an entity from a proto - implementation method'''
        if eid is None:
            eid = self.nextentid
            self.nextentid += 1

        ent = Entity(eid, proto)
        self.newentities[eid] = ent

        # loop until the deps stop changing (when we find all the dependencies)
        deps = set(proto.components)
        while 1:
            newdeps = set(deps)
            for c in deps:
                if c[0] == '@':
                    continue

                cls = getcomponentclass(c)
                for d in cls.depends:
                    newdeps.add(d)

            if newdeps == deps:
                break

            deps = newdeps

        # construct the component classes
        for cname in deps:
            if cname[0] != '@':
                cls = getcomponentclass(cname)
                cls(ent)

        # TODO - tie this with the real global components
        globalcomponents = {
            'sprites' : self.eng.sprites,
            'map' : self.eng.map,
            'datasrc' : self.eng.datasrc,
            'entitymanager' : self,
            'content' : self.eng.content,
            'pathfinder' : self.eng.pathfinder,
            'engine' : self.eng,
            'scripting' : self.eng.scripting,
            'team' : proto.team
        }

        # perform the injection
        for cname in deps:
            if cname[0] != '@':
                cls = getcomponentclass(cname)
                comp = ent.components[cname]
                args = {}
                for c in cls.depends:
                    if c[0] == '@':
                        args[c[1:]] = globalcomponents[c[1:]]
                    else:
                        args[c] = ent.components[c]
                comp.inject(**args)

        # configure the new entity
        ent.configure()

        self.onentitycreated.emit(ent)

        return ent

    def sectorloaded(self, sec):
        '''Load all the entities on the new sector'''
        for eid in sec.entities:
            self.loadentity(eid)

    def step(self):
        ''' Step all entities '''
        self.entities.update(self.newentities)
        self.newentities.clear()

        for ent in self.entities.itervalues():
            ent.step()

    def doorder(self, order):
        ''' Give an order to the relevant entities '''
        if order.type == Order.NONE:
            return

        if order.type == Order.AUTOCOMMAND:
            for eid in order.ents:
                ent = self.get(eid)
                if ent.has('behaviour'):
                    ent.behaviour.autocommand(order.target, order.add)

        elif order.type == Order.ABILITY:
            for eid in order.ents:
                ent = self.get(eid)
                if ent.has('abilities'):
                    ent.abilities.activate(order.idx, order.target)
