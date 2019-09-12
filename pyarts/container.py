'''
Container

This module does the global dependnecy injection used by the entire game.
Right now there are going to be two different DI systems - this global one
and the entity specific one. Perhaps merged the implementations later?
'''

def construct(name):
    print('constructing ', name)
    # find all the dependencies - transitive
    deps = set([name])
    while 1:
        newdeps = set(deps)
        for c in deps:
            cls = getcomponentclass(c)
            for d in cls.depends:
                newdeps.add(d)

        if newdeps == deps:
            break

        deps = newdeps

    # construct the component classes
    components = {}
    for cname in deps:
        cls = getcomponentclass(cname)
        print('creating ', cname)
        components[cname] = cls()

    # perform the injection
    for comp in list(components.values()):
        args = {}
        for cname in type(comp).depends:
            args[cname] = components[cname]
        print('injecting ', comp.__class__.__name__)
        comp.inject(**args)

    print('done')
    return components[name]


_all_components = { }

def component(cls):
    if not hasattr(cls, 'name'):
        cls.name = cls.__name__.lower()
    _all_components[cls.name] = cls
    return cls

def getcomponentclass(name):
    return _all_components[name]
