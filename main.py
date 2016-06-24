import pyglet

from pyarts.ui.screen import Screen
from pyarts.ui.mainmenu import MainMenu
from pyarts.game.settings import Settings

import argparse

def main():
    window = pyglet.window.Window(MainMenu.WIDTH, MainMenu.HEIGHT)
    #window = pyglet.window.Window(fullscreen=True)
    
    Screen.WIDTH = window.width
    Screen.HEIGHT = window.height

    menu = MainMenu()
    menu.activate(window=window)
    pyglet.app.run()

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('-r', '--resolution', help='Set the screen resolution')
    p.add_argument('-f', '--fullscreen', help='Run in fullscreen')
    p.add_argument('-j', '--join', type=str, metavar='ADDR', help='Join a multiplayer game at ADDR')
    p.add_argument('-s', '--server', help='Start a multiplayer server')

    opts, args = p.parse_args()

    settings.join = opts.join
    settings.server = opts.server

    main()
