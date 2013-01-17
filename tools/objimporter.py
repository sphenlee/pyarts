'''
Obj file importer
'''

import sys
import array

verts = []
faces = []

fname = sys.argv[1]

for line in open(fname):
    toks = line.split()
    if toks[0] == 'v':
        x = float(toks[1])
        y = float(toks[3])
        verts.append((x, y))

    elif toks[0] == 'f':
        f = tuple(int(t) - 1 for t in toks[1:3])
        faces.append(f)

data = array.array('f')

for face in faces:
    for idx in face:
        vert = verts[idx]
        data.append(vert[0])
        data.append(vert[1])

print data

fp = open(fname + '.raw', 'wb')
fp.write(data.tostring())
fp.close()
