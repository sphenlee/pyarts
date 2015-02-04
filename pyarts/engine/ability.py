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
    AREA_OF_EFFECT = 'area_of_effect'

    def __init__(self, data, scripting):
        self.name = data['name']
        self.description = data['description']

        code = data['effect']
        if isinstance(code, list):
            code = '\n'.join(code)
        code = 'return ' + code
        self.effect = scripting.lua.dostring(code)
        
        self.type = data['type']

        self.range = data.get('range', 0)
        self.group = data.get('group', False)
        self.cooldown = data.get('cooldown', 0)
        self.cost = Cost.from_data(data['cost'])

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

    def activate(self, me, target):
        if self.type in (Ability.STATIC, Ability.INSTANT):
            self.effect(me)
        elif self.type == Ability.TARGETED:
            if target.isent():
                self.effect(me, target.eid)
        elif self.type == Ability.AREA_OF_EFFECT:
            x, y = target.getpos()
            self.effect(me, x, y)
        else:
            raise Exception('Unknown ability type %s' % self.type)
