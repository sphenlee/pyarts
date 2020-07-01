'''
AbilityAction

High level action for getting an entity to do an action
'''

from .action import Action
from .move import MoveAction
from ..entityproto import EntityProto
from ..target import Target

from pyarts.log import info


class ConstructAction(Action):
    def __init__(self, proto, oncomplete=None):
        self.proto = proto
        self.oncomplete = oncomplete
        self.wait = 200  # TODO - get this from somewhere

    def interruptible(self):
        return False

    def start(self):
        em = self.ent.constructor.entitymanager

        # TODO - cache these protos - and abstract out dynamic proto creation?
        new_proto = EntityProto(self.proto.epid, self.proto.team)
        new_data = self.proto.data.copy()
        new_data['components'] = ['appearance', 'footprint', 'locator',
                                  'variables']
        new_proto.load(new_data)

        self.construction_site = em.create(new_proto)

        self.ent.locator.unplace()
        self.construction_site.locator.place(*self.ent.locator.pos())

        self.construction_site.variables['hp'] = 1
        self.maxhp = self.construction_site.variables.get('hp').max

    def step(self):
        if self.wait:
            self.wait -= 1
            self.construction_site.variables['hp'] = int((1.0 - self.wait / 200.0) * self.maxhp)
        else:
            self.complete_construction()

    def complete_construction(self):
        info('entity %d completing constructions of %s' % (
            self.ent.eid,
            self.proto.name))

        self.ent.locator.replace()
        
        em = self.ent.constructor.entitymanager
        em.destroy(self.construction_site.eid)

        building = em.create(self.proto)

        if self.oncomplete:
            self.oncomplete(building.eid)

        building.locator.place(*self.ent.locator.pos())

        self.done()
        self.ent.actions.now(PostConstructAction(building))


class PostConstructAction(Action):
    def __init__(self, building):
        self.building = building
        self.started = False

    def interruptible(self):
        return False

    def start(self):
        if self.started:
            self.done()

        else:
            self.ent.moving.set_incorporeal(True)

            x, y = self.ent.locator.pos()
            r = self.building.locator.r

            self.ent.actions.now(MoveAction(Target((x + r, y + r))))

            self.started = True

    def stop(self):
        self.ent.moving.set_incorporeal(False)        
