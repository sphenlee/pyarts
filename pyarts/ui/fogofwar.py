'''
FogOfWar
'''

import pyglet
from pyglet.graphics import OrderedGroup

from .util import TextureGroup

class FogOfWar(object):
    def __init__(self, datasrc):
        data = datasrc.gettileset()
        res = datasrc.getresource(data['fogofwar'])

        self.img = pyglet.image.load(res)

        self.tex = self.img.get_texture()
