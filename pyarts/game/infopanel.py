'''
InfoPanel
'''
from pyarts import log

from pyarts.container import component

@component
class InfoPanel(object):
    depends = ['game', 'local', 'datasrc']

    def __init__(self):
        self.data = []

    def inject(self, game, local, datasrc):
        self.game = game
        self.local = local
        self.datasrc = datasrc

    def step(self):
        self.data = []

        for ent in self.game.selection:
            data = {}
            self.data.append(data)

            data['name'] = ent.proto.name

            if ent.has('appearance'):
                data['portrait'] = '/' + self.datasrc.getresource(ent.appearance.portrait)
            else:
                data['portrait'] = None

            if ent.ownedby(self.local.player) and ent.has('variables'):
                vars = ent.variables

                if 'hp' in vars:
                    hp = vars.get('hp')
                    data['hp'] = (hp.val, hp.max)

                if 'mana' in vars:
                    mana = vars.get('mana')
                    data['mana'] = (mana.val, mana.max)
