'''
SingleEntityPanel
'''

import pyglet
from .. import cairosg as sg

HP_RAMP = [
    (1.0, 0.0, 0.0),
    (1.0, 0.5, 0.0),
    (1.0, 1.0, 0.0),
    (0.5, 1.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 1.0, 0.0),
]

class SingleEntityPanel(object):
    def __init__(self, infopanel):
        game = infopanel.game
        self.ent = game.selection[0]

        self.sg = sg.SceneGraph(infopanel.WIDTH, infopanel.HEIGHT).paint(0, 0, 0, 0.8)

        g = sg.Grid(1, 3)

        # portrait and HP display
        g2 = sg.Grid(2, 1)

        r = sg.Rect(10, 10, 128, 128)
        g2.append(r)

        if self.ent.has('appearance'):
            img = infopanel.getimage(self.ent.appearance.portrait)
            r.paint(img)

        if self.ent.has('variables'):
            vars = self.ent.variables

            g3 = sg.Grid(2, 1)
            if 'hp' in vars:
                self.hp = sg.Text('').paint(*HP_RAMP[-1])
                g3.append(self.hp)
            if 'mana' in vars:
                self.mana = sg.Text('').paint(0, 0, 1)
                g3.append(self.mana)

            g2.append(g3)

        g.append(g2)

        self.sg.append(g)


    def step(self):
        if self.ent.has('variables'):
            vars = self.ent.variables

            if 'hp' in vars:
                hp, max = vars.get('hp').val, vars.get('hp').max
                idx = int((float(hp) / max) * 5)
                self.hp.paint(*HP_RAMP[idx])
                self.hp.text = '%d/%d' % (hp, max)
            if 'mana' in vars:
                self.mana.text = '%d/%d' % (vars.get('mana').val, vars.get('mana').max)

        
    def draw(self):
        img = self.sg.getimage()
        s = pyglet.sprite.Sprite(img)
        s.draw()
