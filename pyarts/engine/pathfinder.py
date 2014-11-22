'''
Pathfinder

The pathfinding class - finds paths
'''

import heapq
import math

from .sector import VERTEX_SZ, NEIGHBOURS

def distance(p1, p2):
    return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2

class Pathfinder(object):
    def __init__(self, map):
        self.map = map

    def findpath(self, start, goal, walk, range):
        start = (start[0]/VERTEX_SZ, start[1]/VERTEX_SZ)
        goal = (goal[0]/VERTEX_SZ, goal[1]/VERTEX_SZ)
        range = range/VERTEX_SZ


        def reconstruct_path(current):
            yield current[0]*VERTEX_SZ, current[1]*VERTEX_SZ
            while current in camefrom:
                current = camefrom[current]
                yield current[0]*VERTEX_SZ, current[1]*VERTEX_SZ

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

                sec = self.map.sector_at_point(n[0] * VERTEX_SZ, n[1]*VERTEX_SZ)
                if sec is None:
                    continue

                ox, oy = self.map.pos_to_sector_offset(n[0] * VERTEX_SZ, n[1]*VERTEX_SZ)
                if not sec.pointwalkable(walk, (ox, oy)):
                    continue

                g = gscore[pt] + distance(n, pt)

                if n not in openset or g < gscore[n]:
                    camefrom[n] = pt
                    gscore[n] = g
                    f = g + distance(n, goal)

                    heapq.heappush(openheap, (f, n))
                    openset.add(n)

