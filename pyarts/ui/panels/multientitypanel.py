'''
MultiEntityPanel
'''

import pyglet

class MultiEntityPanel(object):
    def __init__(self, infopanel):
        game = infopanel.game

        self.batch = pyglet.graphics.Batch()
        self.portraits = []
        
        x = 0

        for ent in game.selection:
            if ent.has('appearance'):
                img = infopanel.getimage(ent.appearance.portrait)
                portrait = pyglet.sprite.Sprite(img,
                    20 + x*64, 20,
                    batch=self.batch)

                portrait.scale = 0.5
                self.portraits.append(portrait)

                x += 1

    def step(self):
        pass

    def draw(self):
        self.batch.draw()
