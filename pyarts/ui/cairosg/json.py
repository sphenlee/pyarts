'''
Cairo Scene Graph

Module for building a SceneGraph from a JSON definition
'''

import json
from .scenegraph import *
from .paint import ColourPaint
from .nodes import *

def json_load_string(text):
    obj = json.loads(text)
    return json_load(obj)

def json_load_file(fp):
    obj = json.load(fp)
    return json_load(obj)

def json_load(obj):
    sg = SceneGraph(obj['w'], obj['h'])

    _read_paint(obj, sg)
    _read_canvas(sg, obj, sg)

    return sg

def _read_node(sg, obj):
    type = obj.get('type', 'node type missing')

    if type == 'rect':
        node = _read_rect(obj)
    elif type == 'text':
        node = _read_text(obj)
    elif type == 'grid':
        node = _read_grid(sg, obj)
    elif type == 'vbox':
        node = _read_vbox(sg, obj)
    elif type == 'hbox':
        node = _read_hbox(sg, obj)
    else:
        raise Exception('unknown node type: ' + type)

    if 'id' in obj:
        sg.idmap[obj['id']] = node

    return node


def _read_rect(obj):
    x = obj.get('x')
    y = obj.get('y')
    w = obj.get('w')
    h = obj.get('h')
    r = Rect(x, y, w, h)
    _read_paint(obj, r)
    return r

def _read_text(obj):
    text = obj['text']
    size = obj.get('size')
    try:
        origin = tuple(obj['origin'])
    except KeyError:
        origin = None
    t = Text(text, size, origin)
    _read_paint(obj, t)
    return t

def _read_grid(sg, obj):
    rows = obj.get('rows')
    cols = obj.get('cols')
    g = Grid(rows, cols)
    _read_canvas(sg, obj, g)
    return g

def _read_vbox(sg, obj):
    flex = list(obj.get('flex'))
    v = VBox(flex)
    _read_canvas(sg, obj, v)
    return v

def _read_hbox(sg, obj):
    flex = list(obj.get('flex'))
    h = HBox(flex)
    _read_canvas(sg, obj, h)
    return h

def hex_to_float(h):
    return int(h, 16) / 256.0

def _read_paint(obj, paintable):
    if 'paint' in obj:
        paint = obj['paint']
        if isinstance(paint, basestring):
            if paint[0] == '#':
                r = hex_to_float(paint[1:3])
                g = hex_to_float(paint[3:5])
                b = hex_to_float(paint[5:7])
                a = hex_to_float(paint[7:9])
                paintable.paint(r, g, b, a)
        
def _read_canvas(sg, obj, canvas):
    if 'children' in obj:
        for child in obj['children']:
            node = _read_node(sg, child)
            canvas.append(node)
