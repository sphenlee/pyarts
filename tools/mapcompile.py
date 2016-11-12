'''
Convert a simple text format into the hex format for the map
'''

import sys
import array
import binascii

NUM_TILES = 32
NUM_VERTS = NUM_TILES + 1

tile_lut = {
    'gggg' : 0, 'ssss' : 1, 'wwww' : 2,
    'wgwg' : 3, 'wwgg' : 4, 'gwgw' : 5, 'ggww' : 6,
    'gwgg' : 7, 'gggw' : 8, 'ggwg' : 9, 'wggg' : 10,
    'gwww' : 11, 'wgww' : 12, 'wwwg' : 13, 'wwgw' : 14, 
    'wsws' : 19, 'wwss' : 20, 'swsw' : 21, 'ssww' : 22,
    'swss' : 23, 'sssw' : 24, 'ssws' : 25, 'wsss' : 26,
    'swww' : 27, 'wsww' : 28, 'wwws' : 29, 'wwsw' : 30,
    'gsgs' : 35, 'ggss' : 36, 'sgsg' : 37, 'ssgg' : 38,
    'sgss' : 39, 'sssg' : 40, 'ssgs' : 41, 'gsss' : 42,
    'sggg' : 43, 'gsgg' : 44, 'gggs' : 45, 'ggsg' : 46,
}

G = 0x02 # no water
W = 0x01 # no ground
C = 0x00 # coast, either water or ground

walk_lut = {
    'gggg' : G, 'ssss' : G, 'wwww' : W,
    'wgwg' : C, 'wwgg' : C, 'gwgw' : C, 'ggww' : C,
    'gwgg' : G, 'gggw' : G, 'ggwg' : G, 'wggg' : G,
    'gwww' : W, 'wgww' : W, 'wwwg' : W, 'wwgw' : W, 
    'wsws' : C, 'wwss' : C, 'swsw' : C, 'ssww' : C,
    'swss' : G, 'sssw' : G, 'ssws' : G, 'wsss' : G,
    'swww' : W, 'wsww' : W, 'wwws' : W, 'wwsw' : W,
    'gsgs' : G, 'ggss' : G, 'sgsg' : G, 'ssgg' : G,
    'sgss' : G, 'sssg' : G, 'ssgs' : G, 'gsss' : G,
    'sggg' : G, 'gsgg' : G, 'gggs' : G, 'ggsg' : G,
}


fname = sys.argv[1]
data = open(fname).read().replace('\n', '')

tiles = array.array('B')
tiles.fromstring('\0' * NUM_TILES * NUM_TILES)

walk = array.array('B')
walk.fromstring('\0' * NUM_TILES * NUM_TILES)

for y in range(NUM_TILES):
    for x in range(NUM_TILES):
        nw = data[ x +       y      * NUM_VERTS]
        ne = data[(x + 1) +  y      * NUM_VERTS]
        sw = data[ x +      (y + 1) * NUM_VERTS]
        se = data[(x + 1) + (y + 1) * NUM_VERTS]

        tiles[x + y*NUM_TILES] = tile_lut.get(nw+ne+sw+se, 64)
        walk [x + y*NUM_TILES] = walk_lut.get(nw+ne+sw+se, 64)


fname = sys.argv[2]
open(fname, 'wb').write(binascii.hexlify(tiles.tostring()))

fname = sys.argv[3]
open(fname, 'wb').write(binascii.hexlify(walk.tostring()))

