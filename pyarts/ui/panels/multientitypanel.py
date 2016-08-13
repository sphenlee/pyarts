'''
MultiEntityPanel
'''

from .. import cairosg as sg

def get_layout(w, h):
    return {
        'w': w, 'h': h,
        'paint': '#000000CF',
        'children' : [{
            'type': 'grid',
            'id': 'selected',
            'rows': 2, 'cols': 8,
            'children': []
        }]
    }

class MultiEntityPanel(object):
    def __init__(self, infopanel):
        game = infopanel.game

        self.sg = sg.json_load(get_layout(infopanel.WIDTH, infopanel.HEIGHT))
        
        g = self.sg['selected']
        for ent in game.selection:
            if ent.has('appearance'):
                img = infopanel.imagecache.getimage(ent.appearance.portrait)
                r = sg.Rect().paint(img)
                g.append(r)

    def step(self):
        pass

    def draw(self):
        self.sg.drawat(0, 0)
