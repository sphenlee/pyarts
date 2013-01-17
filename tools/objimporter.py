'''
Obj file importer
'''

import sys
import array
import struct

verts = []
faces = []

fname = sys.argv[1]

minx = float('inf')
miny = float('inf')

maxx = float('-inf')
maxy = float('-inf')

for line in open(fname):
    toks = line.split()
    if toks[0] == 'v':
        x = float(toks[1]) * 10
        y = float(toks[3]) * 10
        if x < minx:
            minx = x
        if y < miny:
            miny = y
        if x > maxx:
            maxx = x
        if y > maxy:
            miny = y

        verts.append((x, y))

    elif toks[0] == 'f':
        f = tuple(int(t) - 1 for t in toks[1:])
        faces.append(f)

vdata = array.array('f')
tdata = array.array('f')

for face in faces:
    for idx in face:
        vert = verts[idx]

        vdata.append(vert[0] - minx)
        vdata.append(vert[1] - miny)

        tdata.append((vert[0] - minx) / (maxx - minx))
        tdata.append((vert[1] - miny) / (maxx - minx))

print vdata
print tdata

s = struct.Struct('I')

fp = open(fname + '.raw', 'wb')
fp.write(s.pack(len(vdata)))
fp.write(vdata.tostring())
fp.write(tdata.tostring())
fp.close()
