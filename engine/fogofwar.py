'''
FogOfWar
'''

import pyglet

from ui.util import TextureGroup

class FogOfWar(object):
    def __init__(self, datasrc):
        data = datasrc.gettileset()
        res = datasrc.getresource(data['fogofwar'])

        self.img = pyglet.image.load(res)

        self.group = TextureGroup(self.img.get_texture())

    coords = [
        '0000', '0001', '0011', '0010', '0101', '1110', '1101', '1010',
        '1111', '0100', '1100', '1000', '0110', '1011', '0111', '1001'
    ]

    def gettile(self, a, b, c, d):
        s = '%d%d%d%d' % (a, b, c, d)
        idx = self.coords.index(s)
        return divmod(idx, 8)
