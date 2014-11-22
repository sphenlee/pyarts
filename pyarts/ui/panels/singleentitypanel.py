'''
SingleEntityPanel
'''

import pyglet

class SingleEntityPanel(object):
    def __init__(self, infopanel):
        game = infopanel.game
        ent = game.engine.entities.get(game.selection[0])

        self.batch = pyglet.graphics.Batch()
        self.label = pyglet.text.Label(ent.proto.name,
            x=20 + 128 + 10, y=100,
            batch=self.batch)

        if ent.has('appearance'):
            img = infopanel.getimage(ent.appearance.portrait)
            self.portrait = pyglet.sprite.Sprite(img,
                20, 20,
                batch=self.batch)
        
    def draw(self):
        self.batch.draw()
