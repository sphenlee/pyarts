'''
Container

This module does the global dependnecy injection used by the entire game.
Right now there are going to be two different DI systems - this global one
and the entity specific one. Perhaps merged the implementations later?
'''

from pyarts.log import trace, info

def get_deps(cls):
    deps = cls.depends
    if isinstance(deps, list):
        return deps
    else:
        return deps()


def construct(name):
    info('constructing {0}', name)
    # find all the dependencies - transitive
    deps = set([name])
    while 1:
        newdeps = set(deps)
        for c in deps:
            cls = getcomponentclass(c)
            for d in get_deps(cls):
                newdeps.add(d)

        if newdeps == deps:
            break

        deps = newdeps

    # construct the component classes
    components = {}
    for cname in deps:
        cls = getcomponentclass(cname)
        trace('creating {0}', cname)
        components[cname] = cls()

    # perform the injection
    for comp in list(components.values()):
        args = {}
        for cname in get_deps(type(comp)):
            args[cname] = components[cname]
        trace('injecting {0}', comp.__class__.__name__)
        comp.inject(**args)

    info('done')
    return components[name]


_all_components = { }

def component(cls):
    if hasattr(cls, 'name'):
        name = cls.name
    else:
        name = cls.__name__.lower()
        
    _all_components[name] = cls
    return cls

def getcomponentclass(name):
    return _all_components[name]
