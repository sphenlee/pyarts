'''
Tileset

Loads the textures for the tiles on the map
'''

import pyglet

from ui.util import TextureGroup

class Tileset(object):
    def __init__(self, datasrc):
        data = datasrc.gettileset()

        res = datasrc.getresource(data['texture'])
        self.img = pyglet.image.load(res)

        self.group = TextureGroup(self.img.get_texture())