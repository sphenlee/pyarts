'''
Root
This is the component that instantiates the entire game
'''

#__all__ = ['Root']

from .container import component

# TODO
#mapfile = 'maps/test/map.json'

# @component
# class Root(object):
#     depends = ['settings', 'datasrc', 'game', 'gamestate', 'maprenderer']

#     def __init__(self):
#         pass

#     def inject(self, **kwargs):
#         self.__dict__.update(kwargs)

#     def load(self, settings=None):
#         
#         self.settings.load(settings)
        
#     def save(self, datasink):
#         self.game.save(datasink)
        
#     def update(self):
#         self.gamestate.step()

from yarts import Root
component(Root)
