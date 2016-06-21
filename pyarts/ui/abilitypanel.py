'''
AbilitiesPanel

Renders the buttons for entity abilities
'''

from . import cairosg as sg

class AbilityPanel(object):
    WIDTH = 64*2
    HEIGHT = 64*3

    def __init__(self):
        self.sg = sg.SceneGraph().paint(0, 0, 0, 0.8)
        
        self.grid = sg.Grid(3, 2)
        