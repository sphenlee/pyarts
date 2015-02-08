import sys
sys.path.insert(0, '../pyglet')

import pyglet

from pyarts.ui.screen import Screen
from pyarts.ui.mainmenu import MainMenu

def main():
    #window = pyglet.window.Window(MainMenu.WIDTH, MainMenu.HEIGHT)
    window = pyglet.window.Window(fullscreen=True)
    
    Screen.WIDTH = window.width
    Screen.HEIGHT = window.height

    menu = MainMenu(window=window)
    menu.activate()
    pyglet.app.run()

if __name__ == '__main__':
    main()
