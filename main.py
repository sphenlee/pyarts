import pyglet

from engine.game import Game

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

        self.game = Game()

        pyglet.app.run()

if __name__ == '__main__':
    main = Main()
    main.run()
