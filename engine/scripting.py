'''
Scripting

Various functions that get exposed to Lua
'''

from lua import lua

@lua.func
def print_(*args):
    ''' Simulate Lua's print which tab separates args '''
    print '\t'.join(str(a) for a in args)

def setup(lua):
    lua.setglobal('print', print_)
