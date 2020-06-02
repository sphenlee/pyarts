'''
InfoPanel
'''



from .singleentitypanel import SingleEntityPanel
from .multientitypanel import MultiEntityPanel

from pyarts.container import component

@component
class InfoPanel(object):
    depends = ['game', 'local', 'imagecache', 'settings']

    def __init__(self):
        self.display = None

    def inject(self, game, local, imagecache, settings):
        self.game = game
        self.local = local
        self.imagecache = imagecache

        self.game.onselectionchange.add(self.update)

        settings.onload.add(self.onload)

    def onload(self, settings):
        self.WIDTH = settings.width // 2
        self.HEIGHT = settings.height // 4

    def step(self):
        if self.display:
            self.display.step()

    def update(self):
        if len(self.game.selection) == 1:
            self.display = SingleEntityPanel(self)
        elif len(self.game.selection) > 1:
            self.display = MultiEntityPanel(self)
        else:
            self.display = None

    def render(self):
        if self.display:
            return self.display.render()

    def destination(self, w, h):
        return (0, h - self.HEIGHT)
