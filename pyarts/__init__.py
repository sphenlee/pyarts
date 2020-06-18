# import component classes

from .game import *
from .engine import *
from .log import *


from .container import component, construct


# register components implemented in Rust

from yarts import MapRenderer, GameUi, Root

component(MapRenderer)
component(GameUi)
component(Root)
