'''
Resource

Component to allow an entity to be a source of resources.
This is similar to a variable but not a complex (for things
    like a Gold Mine having stats and variables is overkill)
'''

from .component import Component, register

@register
class Resource(Component):
    depends = []

    def configure(self, data):
        pass

    def load(self, data):
        self.resource = data['resource']
    
    def save(self):
        return { 
            'resource' : self.resource
        }
