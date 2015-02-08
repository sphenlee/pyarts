'''
SingleEntityPanel
'''

import pyglet

HP_RAMP = [
    (0xFF, 0x00, 0x00, 0xFF),
    (0xFF, 0x7F, 0x00, 0xFF),
    (0xFF, 0xFF, 0x00, 0xFF),
    (0x7F, 0xFF, 0x00, 0xFF),
    (0x00, 0xFF, 0x00, 0xFF),
    (0x00, 0xFF, 0x00, 0xFF),
]

class SingleEntityPanel(object):
    def __init__(self, infopanel):
        game = infopanel.game
        self.ent = game.engine.entities.get(game.selection[0])

        self.batch = pyglet.graphics.Batch()
        self.name = pyglet.text.Label(self.ent.proto.name,
            x=20 + 128 + 10, y=100,
            batch=self.batch)

        if self.ent.has('appearance'):
            img = infopanel.getimage(self.ent.appearance.portrait)
            self.portrait = pyglet.sprite.Sprite(img,
                20, 20,
                batch=self.batch)

        if self.ent.has('variables'):
            vars = self.ent.variables

            if 'hp' in vars:
                self.hp = pyglet.text.Label('',
                    x=20 + 128 + 10, y=80,
                    batch=self.batch)
            if 'mana' in vars:
                self.mana = pyglet.text.Label('',
                    x=20 + 128 + 10, y=60,
                    batch=self.batch)
                self.mana.color = (0x00, 0x00, 0xFF, 0xFF)

    def step(self):
        if self.ent.has('variables'):
            vars = self.ent.variables

            if 'hp' in vars:
                hp, max = vars['hp'], vars.getmax('hp')
                idx = int((float(hp) / max) * 5)
                self.hp.color = HP_RAMP[idx]
                self.hp.text = '%d/%d' % (hp, max)
            if 'mana' in vars:
                self.mana.text = '%d/%d' % (vars['mana'], vars.getmax('mana'))

        
    def draw(self):
        self.batch.draw()
