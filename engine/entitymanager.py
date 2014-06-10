'''
EntityManager

Container holding all of the entities
'''

from .components.component import getcomponentclass
from .entity import Entity
from .order import Order

class EntityManager(object):
    def __init__(self, eng):
        self.eng = eng
        self.datasrc = eng.datasrc
        self.nextentid = 0
        self.entities = { } # entid -> entitiy

    def get(self, eid):
        return self.entities[eid]

    def load(self):
        data = self.datasrc.getentities()
        for eid, edata in data.iteritems():
            team = self.eng.getteam(edata['team'])
            proto = team.getproto(edata['proto'])
            ent = self.create(proto, eid=int(eid))
            ent.load(edata)

        self.nextentid = self.datasrc.getmisc('entities.nextentid', 1)

    def save(self, sink):
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

        # perform the dependency injection
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

        for cname in deps:
            if cname[0] != '@':
                cls = getcomponentclass(cname)
                cls(ent)

        globalcomponents = {
            'renderer' : self.eng.renderer,
            'map' : self.eng.map,
            'datasrc' : self.eng.datasrc,
            'entitymanager' : self
        }

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

        ent.configure()

        return ent


    def step(self):
        for ent in self.entities.itervalues():
            ent.step()

    def doorder(self, order):
        if order.type == Order.NONE:
            return

        if order.type == Order.AUTOCOMMAND:
            for eid in order.ents:
                ent = self.get(eid)
                if ent.has('behaviour'):
                    # behaviour depends on actions, so no need to check for both
                    action = ent.behaviour.autocommand(order.target)
                    ent.actions.give(action)
