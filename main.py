import pyglet

from engine.game import Game
from engine.datasource import DataSource

class Main(object):
    '''
    The main object!
    '''
    def on_draw(self):
        self.window.clear()
        self.game.render()

    def run(self):
        self.window = pyglet.window.Window(800, 600)
        self.window.push_handlers(self)

        mapfile = 'maps/test/map.json'
        self.datasrc = DataSource(mapfile, mapfile, mapfile)
        self.game = Game(self.datasrc)
        self.game.load()

        pyglet.app.run()

if __name__ == '__main__':
    main = Main()
    main.run()
