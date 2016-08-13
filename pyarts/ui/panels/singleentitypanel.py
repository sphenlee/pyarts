'''
SingleEntityPanel
'''

from .. import cairosg as sg

HP_RAMP = [
    (1.0, 0.0, 0.0),
    (1.0, 0.5, 0.0),
    (1.0, 1.0, 0.0),
    (0.5, 1.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 1.0, 0.0),
]

def get_layout(w, h):
    return {
        'w': w, 'h': h,
        'paint': '#000000CF',
        'children' : [{
            'type': 'hbox',
            'flex': [1, 1, 1],
            'children': [{
                'type': 'vbox',
                'flex': [4, 1, 1],
                'children': [{
                    'type': 'rect',
                    'id': 'portrait'
                }, {
                    'type': 'text',
                    'id': 'hp',
                    'text': ''
                }, {
                    'type': 'text',
                    'id': 'mana',
                    'paint': '#3F7FFFFF', # light blue
                    'text': ''
                }]
            }]
        }]
    }

class SingleEntityPanel(object):
    def __init__(self, infopanel):
        game = infopanel.game
        self.ent = game.selection[0]

        self.sg = sg.json_load(get_layout(infopanel.WIDTH, infopanel.HEIGHT))

        if self.ent.has('appearance'):
            img = infopanel.imagecache.getimage(self.ent.appearance.portrait)
            r = self.sg['portrait']
            r.paint(img)

        self.showvars = (self.ent.ownedby(game.localplayer) and self.ent.has('variables'))

        if self.showvars:
            vars = self.ent.variables

            if 'hp' in vars:
                self.hp = self.sg['hp']
            if 'mana' in vars:
                self.mana = self.sg['mana']


    def step(self):
        if self.showvars:
            vars = self.ent.variables

            if 'hp' in vars:
                hp, max = vars.get('hp').val, vars.get('hp').max
                idx = int((float(hp) / max) * 5)
                self.hp.paint(*HP_RAMP[idx])
                self.hp.text = '%d/%d' % (hp, max)
            if 'mana' in vars:
                self.mana.text = '%d/%d' % (vars.get('mana').val, vars.get('mana').max)

        
    def draw(self):
        self.sg.drawat(0, 0)
