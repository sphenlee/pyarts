# import component classes

from .game import *
from .engine import *
from .root import *
#from .ui import *


from .container import component, construct


# register components implemented in Rust

from yarts import MapRenderer
component(MapRenderer)
