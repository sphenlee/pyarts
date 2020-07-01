'''
Ability

An ability is a special action an entity can do.
They are bound to the buttons
'''
from pyarts.container import dynamic_component
from pyarts.log import warn

from .resource import Cost


@dynamic_component
class Ability(object):
    STATIC = 'static'            
    INSTANT = 'instant'
    TARGETED = 'targeted'
    BUILD = 'build'
    AREA_OF_EFFECT = 'area_of_effect'
    ACTIVITY = 'activity'

    depends = ['scripting']

    def __init__(self, data):
        self.data = data

        self.name = data['name']
        self.description = data['description']

        self.type = data['type']

        self.range = data.get('range', None)
        self.group = data.get('group', False)
        self.queue = data.get('queue', False)
        self.wait = data.get('wait', 0)
        self.cooldown = data.get('cooldown', 0)
        self.cost = Cost.from_data(data['cost'])

        if self.type == Ability.BUILD:
            self.proto = data['proto']

        self.image = data['image']

    def inject(self, scripting):
        self.effect = scripting.code(self.data['effect'])

        self.onstart = scripting.code(self.data['onstart']) \
            if 'onstart' in self.data else None
        self.onstop = scripting.code(self.data['onstop']) \
            if 'onstop' in self.data else None

    def check_cost(self, ent):
        if self.cost.is_town_cost():
            if not ent.has('town'):
                warn('ignoring out of town cost')
                return True

            res = ent.town.town.resources
            if not res.sufficient(self.cost):
                return False

        if self.cost.is_entity_cost():
            if not ent.has('variables'):
                return False
            vars = ent.variables
            if 'mana' not in vars or vars['mana'] < self.cost.mana:
                return False

        return True

    def deduct_cost(self, ent):
        if self.cost.is_town_cost():
            if not ent.has('town'):
                warn('ignoring out of town cost')
                return

            res = ent.town.town.resources
            res.deduct(self.cost)

        if self.cost.is_entity_cost():
            ent.variables['mana'] -= self.cost.mana

    def activate(self, me, target):
        if self.type in (Ability.STATIC, Ability.INSTANT, Ability.ACTIVITY):
            self.effect(me.eid)
        elif self.type in (Ability.TARGETED,):
            if target.isent():
                self.effect(me.eid, target.ent.eid)
        elif self.type in (Ability.AREA_OF_EFFECT,  Ability.BUILD):
            x, y = target.getpos()
            self.effect(me.eid, x, y)
        else:
            raise Exception('Unknown ability type %s' % self.type)
