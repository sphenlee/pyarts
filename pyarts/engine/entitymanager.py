'''
EntityManager

Container holding all of the entities
'''

from .components.component import getcomponentclass
from .entity import Entity
from .order import Order
from .actions import AbilityAction

class EntityManager(object):
    def __init__(self, eng):
        self.eng = eng
        self.datasrc = eng.datasrc
        self.nextentid = 0
        self.entities = { } # entid -> entitiy

        self.eng.map.onsectorloaded.add(self.sectorloaded)

    def get(self, eid):
        ''' Get an entity by ID '''
        return self.entities[eid]

    def load(self):
        ''' Individual entities are loaded as the map loads sectors, juts grab misc data here '''
        self.nextentid = self.datasrc.getmisc('entities.nextentid', 1)

    def loadentity(self, eid):
        ''' Load a single entity by eid '''
        data = self.datasrc.getentity(eid)
        team = self.eng.getteam(data['team'])
        proto = team.getproto(data['proto'])
        ent = self.create(proto, eid=int(eid))
        ent.load(data)

    def save(self, sink):
        ''' Save all the entities '''
        for eid, ent in self.entities.iteritems():
            data = ent.save()
            sink.addentity(eid, data)

        sink.setmisc('entities.nextentid', self.nextentid)

    def create(self, proto, eid=None):
        '''Create an entity from a proto'''
        if eid is None:
            eid = self.nextentid
            self.nextentid += 1

        ent = Entity(eid, proto)
        self.entities[eid] = ent

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

        globalcomponents = {
            'sprites' : self.eng.sprites,
            'map' : self.eng.map,
            'datasrc' : self.eng.datasrc,
            'entitymanager' : self,
            'content' : self.eng.content,
            'pathfinder' : self.eng.pathfinder
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

        return ent

    def sectorloaded(self, sec):
        '''Load all the entities on the new sector'''
        for eid in sec.entities:
            self.loadentity(eid)

    def step(self):
        ''' Step all entities '''
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
