'''
InfoPanel
'''
from pyarts import log

from pyarts.container import component

@component
class InfoPanel(object):
    depends = ['game', 'local']

    def __init__(self):
        self.data = []

    def inject(self, game, local):
        self.game = game
        self.local = local

    def step(self):
        try:
            self.do_step()
        except Exception as e:
            import traceback
            traceback.print_exc()

    def do_step(self):
        self.data = []

        for ent in self.game.selection:
            data = {}
            self.data.append(data)

            data['name'] = ent.proto.name
            
            if ent.has('appearance'):
                data['portrait'] = ent.appearance.portrait

            if ent.ownedby(self.local.player) and ent.has('variables'):
                vars = ent.variables

                if 'hp' in vars:
                    hp = vars.get('hp')
                    data['hp'] = (hp.val, hp.max)                    

                if 'mana' in vars:
                    mana = vars.get('mana')
                    data['mana'] = (mana.val, mana.max)
