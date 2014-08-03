'''
FogOfWar
'''

import pyglet

from .util import TextureGroup

class FogOfWar(object):
    def __init__(self, datasrc):
        data = datasrc.gettileset()
        res = datasrc.getresource(data['fogofwar'])

        self.img = pyglet.image.load(res)

        self.group = TextureGroup(self.img.get_texture())

    coords = [
        '0000', '0002', '0022', '0020', '0202', '2220', '2202', '2020',
        '2222', '0200', '2200', '2000', '0220', '2022', '0222', '2002',
        
        '1111', '1112', '1122', '1121', '1212', '2221', '2212', '2121',
        '2222', '1211', '2211', '2111', '1221', '2122', '1222', '2112',
        
        '0000', '0001', '0011', '0010', '0101', '1110', '1101', '1010',
        '1111', '0100', '1100', '1000', '0110', '1011', '0111', '1001'
    ]

    def gettile(self, a, b, c, d, e, f, g, h):
        # no, I'm not trying to obfuscate this code...
        def x(j, k):
            if j:
                return '2'
            if k:
                return '1'
            return '0'

        s = x(a, e) + x(b, f) + x(c, g) + x(d, h)
        try:
            idx = self.coords.index(s)
            return divmod(idx, 8)
        except ValueError:
            print 'missing fog tile', s
            return 0, 0
