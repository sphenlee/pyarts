'''
Ability

An ability is a special action an entity can do.
They are bound to the buttons
'''

class Ability(object):
    STATIC = 1
    INSTANT = 2
    TARGETED = 3
    AREA_OF_EFFECT = 4

    def __init__(self, data):
        self.name = data['name']
        self.description = data['description']

        self.effect = data['effect']

        self.type = {
            'static' : Ability.STATIC,
            'instant' : Ability.INSTANT,
            'targeted' : Ability.TARGETED,
            'area_of_effect' : Ability.AREA_OF_EFFECT,
        }[data['type']]

        self.range = data.get('range', 0)
        self.group = data.get('group', False)
        self.cooldown = data.get('cooldown', 0)
        self.cost = data['cost']

        self.image = data['image']
