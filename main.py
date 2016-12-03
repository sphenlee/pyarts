import pyglet

from pyarts.ui.screen import Screen
from pyarts.ui.mainmenu import MainMenu

from pyarts.container import construct

import argparse

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('-r', '--resolution', help='Set the screen resolution')
    p.add_argument('-f', '--fullscreen', help='Run in fullscreen')
    p.add_argument('-j', '--join', type=str, metavar='ADDR', help='Join a multiplayer game at ADDR')
    p.add_argument('-s', '--server', action='store_true', help='Start a multiplayer server')

    opts = p.parse_args()

    window = pyglet.window.Window(MainMenu.WIDTH, MainMenu.HEIGHT)
    #window = pyglet.window.Window(fullscreen=True)
    
    Screen.WIDTH = window.width
    Screen.HEIGHT = window.height

    if opts.join:
        mapfile = 'maps/test/map.json'
        root = construct('root')
        root.load({
            'localpid': 1,
            'join': True,
            'data': {
                'core': mapfile,
                'map': mapfile,
                'save': mapfile
            }
        })
        root.run(window)

    elif opts.server:
        mapfile = 'maps/test/map.json'
        root = construct('root')
        root.load({
            'localpid': 0,
            'server': True,
            'data': {
                'core': mapfile,
                'map': mapfile,
                'save': mapfile
            }
        })
        root.run(window)

    else:
        menu = MainMenu()
        menu.activate(window=window)

    pyglet.app.run()