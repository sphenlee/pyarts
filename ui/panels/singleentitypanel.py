'''
SingleEntityPanel
'''

import pyglet

class SingleEntityPanel(object):
    def __init__(self, game):
        self.game = game
        self.ent = game.engine.entities.get(game.selection[0])
        self.label = pyglet.text.Label(self.ent.proto.name)
        
    def draw(self):
        self.label.x = 100
        self.label.y = 100
        self.label.draw()
