'''
ModeStack

Hold the stack of modes - used for complex UI interactions like building
and targeted abilities
'''

from .modes import *

from pyarts.engine.event import Event
from pyarts.container import component


@component
class ModeStack(object):
    depends = ['game', 'components']

    def __init__(self):
        self.modes = []
        self.onmodechange = Event()

    def inject(self, game, components):
        self.game = game
        self.components = components
        self.push_mode('normalmode')

    @property
    def mode(self):
        '''
        Get the current mode - modes decide what the
        mouse buttons and keys do
        '''
        return self.modes[-1]

    def enter_mode(self):
        self.mode.setup(self, self.game)
        self.mode.enter()
        self.onmodechange.emit(self.mode.__class__.__name__)

    def push_mode(self, name, *args, **kwargs):
        ''' Enter a new mode '''
        mode = self.components.construct(name, *args, **kwargs)

        if self.modes:
            self.mode.exit()

        self.modes.append(mode)
        self.enter_mode()

    def pop_mode(self):
        ''' Return to the previous mode '''
        self.mode.exit()
        self.modes.pop()

        self.enter_mode()
