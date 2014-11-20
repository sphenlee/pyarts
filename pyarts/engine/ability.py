'''
Ability

An ability is a special action an entity can do.
They are bound to the buttons
'''

class Ability(object):
    STATIC = 'static'            
    INSTANT = 'instant'
    TARGETED = 'targeted'
    AREA_OF_EFFECT = 'area_of_effect'

    def __init__(self, data, lua):
        self.name = data['name']
        self.description = data['description']

        code = data['effect']
        if isinstance(code, list):
            code = '\n'.join(code)
        code = 'return ' + code
        self.effect = lua.dostring(code)
        
        self.type = data['type']

        self.range = data.get('range', 0)
        self.group = data.get('group', False)
        self.cooldown = data.get('cooldown', 0)
        self.cost = data['cost']

        self.image = data['image']

    def activate(self, me, target):
        if self.type in (Ability.STATIC, Ability.INSTANT):
            self.effect(me)
        elif self.type == Ability.TARGETED:
            if target.isent():
                self.effect(me, target.eid)
        elif self.type == Ability.AREA_OF_EFFECT:
            x, y = target.getpos()
            self.effect(me, x, y)
