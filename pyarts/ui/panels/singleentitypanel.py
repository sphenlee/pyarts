'''
SingleEntityPanel
'''

import pyglet

class SingleEntityPanel(object):
    def __init__(self, infopanel):
        game = infopanel.game
        self.ent = game.engine.entities.get(game.selection[0])

        self.batch = pyglet.graphics.Batch()
        self.label = pyglet.text.Label(self.ent.proto.name,
            x=20 + 128 + 10, y=100,
            batch=self.batch)

        if self.ent.has('appearance'):
            img = infopanel.getimage(self.ent.appearance.portrait)
            self.portrait = pyglet.sprite.Sprite(img,
                20, 20,
                batch=self.batch)
        
    def draw(self):
        self.batch.draw()
