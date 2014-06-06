'''
EntityManager

Container holding all of the entities
'''

from .components.component import getcomponentclass
from .entity import Entity

class EntityManager(object):
    def __init__(self, eng):
        self.eng = eng
        self.datasrc = eng.datasrc
        self.nextentid = 0
        self.entities = { } # entid -> entitiy

    def load(self):
        data = self.datasrc.getentities()
        for eid, edata in data.iteritems():
            team = self.eng.getteam(edata['team'])
            proto = team.getproto(edata['proto'])
            ent = self.create(proto, eid=eid)
            ent.load(edata)

    def create(self, proto, eid=None):
        '''Create an entity from a proto'''
        if eid is None:
            eid = self.nextentid
            self.nextentid += 1

        ent = Entity(eid, proto)

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
            'datasrc' : self.eng.datasrc
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

        return ent
