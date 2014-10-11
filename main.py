import sys
sys.path.insert(0, '../pyglet')

import pyglet

from ui.mainmenu import MainMenu

def main():
    window = pyglet.window.Window(MainMenu.WIDTH, MainMenu.HEIGHT)
    #window = pyglet.window.Window(fullscreen=True)
    
    menu = MainMenu(window=window)
    menu.activate()
    pyglet.app.run()

if __name__ == '__main__':
    main()
