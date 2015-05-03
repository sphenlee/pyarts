'''
Pathfinder

The pathfinding class - finds paths
'''

import heapq
import math

from .sector import VERTEX_SZ, NEIGHBOURS

from pyarts.container import component

def distance(p1, p2):
    return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2

@component
class Pathfinder(object):
    depends = ['map']

    def inject(self, map):
        self.map = map

    def findpath(self, start, goal, walk, range):
        start = self.map.pos_to_cell(*start)
        goal = self.map.pos_to_cell(*goal)
        range = range/VERTEX_SZ


        def reconstruct_path(current):
            yield self.map.cell_to_pos(*current)
            while current in camefrom:
                current = camefrom[current]
                yield self.map.cell_to_pos(*current)

        closed = set()
        openheap = [(distance(start, goal), start)]
        openset = set((start,))
        camefrom = {}
        gscore = {}

        gscore[start] = 0

        while openset:
            f, pt = heapq.heappop(openheap)
            if pt in closed:
                continue

            openset.discard(pt)
            closed.add(pt)

            if distance(pt, goal) <= range:
                return reconstruct_path(pt)

            for (dx, dy) in NEIGHBOURS:
                n = (pt[0] + dx, pt[1] + dy)

                if n in closed:
                    continue

                sec = self.map.sector_at_cell(*n)
                if sec is None:
                    continue

                offs = self.map.cell_to_offset(*n)
                if not sec.cellwalkable(walk, offs):
                    continue

                g = gscore[pt] + distance(n, pt)

                if n not in openset or g < gscore[n]:
                    camefrom[n] = pt
                    gscore[n] = g
                    f = g + distance(n, goal)

                    heapq.heappush(openheap, (f, n))
                    openset.add(n)

