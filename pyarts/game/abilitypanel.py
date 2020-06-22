'''
AbilityPanel

Renders the buttons for entity abilities
'''

from pyarts.log import debug
from pyarts.container import component

NUM_ABILITIES = 10

@component
class AbilityPanel(object):
    depends = ['game', 'local', 'datasrc']

    def __init__(self):
        self.data = []

    def inject(self, game, local, datasrc):
        self.game = game
        self.local = local
        self.datasrc = datasrc

        self.game.onselectionchange.add(self.update)

    def update(self):
        self.data = []

        try:
            ent = self.game.selection[0]
        except IndexError:
            ent = None

        if ent and ent.has('abilities') and ent.ownedby(self.local.player):

            for ai in ent.abilities:
                data = {}
                data['image'] = '/' + self.datasrc.getresource(ai.ability.image)
                data['description'] = ai.ability.description


                if ai.ability.cooldown > 0:
                    percent = float(ai.cooldown) / ai.ability.cooldown
                    data['cooldown'] = percent
                
                self.data.append(data)


    def step(self):
        if self.game.selection:
            ent = self.game.selection[0]
            if ent.has('abilities') and ent.ownedby(self.local.player):
                ab = ent.abilities
                
                for ai, data in zip(ent.abilities, self.data):
                    if ai.ability.cooldown > 0:
                        percent = float(ai.cooldown) / ai.ability.cooldown
                        data['cooldown'] = percent

