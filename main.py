import pyglet

from ui.mainmenu import MainMenu

def main():
    window = pyglet.window.Window(800, 600)
    
    menu = MainMenu(window=window)
    menu.activate()
    pyglet.app.run()

if __name__ == '__main__':
    main()