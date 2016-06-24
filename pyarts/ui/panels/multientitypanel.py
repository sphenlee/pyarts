'''
MultiEntityPanel
'''

from .. import cairosg as sg

class MultiEntityPanel(object):
    def __init__(self, infopanel):
        game = infopanel.game

        self.sg = sg.SceneGraph(infopanel.WIDTH, infopanel.HEIGHT).paint(0, 0, 0, 0.8)
        
        g = sg.Grid(2, 8)
        self.sg.append(g)

        for ent in game.selection:
            if ent.has('appearance'):
                img = infopanel.imagecache.getimage(ent.appearance.portrait)
                r = sg.Rect(20, 20, 64).paint(img)
                g.append(r)

    def step(self):
        pass

    def draw(self):
        self.sg.drawat(0, 0)
