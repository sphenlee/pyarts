'''
Constructor

Component for entities that can construct buildings
'''

from .component import Component, register

@register
class Constructor(Component):
    depends = ['actions', '@entitymanager', 'moving', 'locator']

    def inject(self, entitymanager, **kwargs):
    	self.entitymanager = entitymanager

    def configure(self, data):
    	pass

    def load(self, data):
    	pass

    def save(self):
    	pass
