'''
Resource

Component to allow an entity to be a source of resources.
This is similar to a variable but not as complex (for things
    like a Gold Mine having stats and variables is overkill)

The component triggers a function when the resource runs out,
this can for example destroy the entity, or change it's behaviour.
'''

from .component import Component, register

@register
class Resource(Component):
    depends = ['@scripting']

    def inject(self, scripting):
        self.scripting = scripting

    def configure(self, data):
        if data is None:
            data = {} # hack...

        self.kind = data.get('kind', 'resource')
        self.quantity = data.get('quantity', 0)
        self.unplace_harvester = data.get('unplace_harvester', False)

        if 'deplete' in data:
            self.deplete = self.scripting.code(data['deplete'])
        else:
            self.deplete = None

    def load(self, data):
        if data:
            self.quantity = data.get('quantity', self.quantity)
    
    def save(self):
        return { 
            'quantity' : self.quantity
        }

    def deduct(self, amt):
        self.quantity -= amt
        if self.quantity <= 0:
            if self.deplete:
                self.deplete(self.eid)
