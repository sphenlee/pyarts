'''
PyLua

Wrapper for Python classes in Lua
'''

def expose(func):
    func.lua_exposed = True
    return func

def object(cls):
    