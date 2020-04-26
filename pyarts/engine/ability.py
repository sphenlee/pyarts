'''
Ability

An ability is a special action an entity can do.
They are bound to the buttons
'''

from .resource import Cost

class Ability(object):
    STATIC = 'static'            
    INSTANT = 'instant'
    TARGETED = 'targeted'
    BUILD = 'build'
    AREA_OF_EFFECT = 'area_of_effect'
    ACTIVITY = 'activity'

    def __init__(self, data, scripting):
        self.name = data['name']
        self.description = data['description']

        self.type = data['type']

        self.effect = scripting.code(data['effect'])

        self.onstart = scripting.code(data['onstart']) if 'onstart' in data else None
        self.onstop = scripting.code(data['onstop']) if 'onstop' in data else None
        
        self.range = data.get('range', None)
        self.group = data.get('group', False)
        self.queue = data.get('queue', False)
        self.wait = data.get('wait', 0)
        self.cooldown = data.get('cooldown', 0)
        self.cost = Cost.from_data(data['cost'])

        if self.type == Ability.BUILD:
            self.ghost = data['ghost']

        self.image = data['image']

    def check_cost(self, ent):
        if self.cost.is_town_cost():
            if not ent.has('town'):
                return False
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
