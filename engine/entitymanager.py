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

    def get(self, eid):
        ''' Get an entity by ID '''
        return self.entities[eid]

    def load(self):
        ''' Load all the entities '''
        data = self.datasrc.getentities()
        for eid, edata in data.iteritems():
            team = self.eng.getteam(edata['team'])
            proto = team.getproto(edata['proto'])
            ent = self.create(proto, eid=int(eid))
            ent.load(edata)

        self.nextentid = self.datasrc.getmisc('entities.nextentid', 1)

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
            'renderer' : self.eng.renderer,
            'map' : self.eng.map,
            'datasrc' : self.eng.datasrc,
            'entitymanager' : self,
            'content' : self.eng.content
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
                    ent.behaviour.autocommand(order.target)

        elif order.type == Order.ABILITY:
            for eid in order.ents:
                ent = self.get(eid)
                if ent.has('abilities'):
                    ent.abilities.activate(order.idx, order.target)
