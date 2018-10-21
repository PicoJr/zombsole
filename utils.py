# coding: utf-8
import math
import networkx as nx


def to_position(something):
    """Converts something (thing/position) to a position tuple."""
    if isinstance(something, tuple):
        return something
    else:
        return something.position


def distance(a, b):
    """Calculates distance between two positions or things."""
    x1, y1 = to_position(a)
    x2, y2 = to_position(b)

    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    return math.sqrt((dx ** 2) + (dy ** 2))

def manhattan(a, b):
    """Calculates manhattan distance between two positions"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def sort_by_distance(something, others):
    by_distance = lambda other: distance(something, other)
    return sorted(others, key=by_distance)


def closest(something, others):
    """Returns the closest other to something (things/positions)."""
    if others:
        return sort_by_distance(something, others)[0]


def adjacent_positions(something):
    """Calculates the 4 adjacent positions of something (thing/position)."""
    position = to_position(something)
    deltas = ((0, 1),
              (0, -1),
              (1, 0),
              (-1, 0))

    return [(position[0] + delta[0],
             position[1] + delta[1])
            for delta in deltas]


def possible_moves(something, things):
    """Calculates the possible moves for a thing."""
    positions = [position for position in adjacent_positions(something)
                 if things.get(position) is None]

    return positions

def astar_path(source, target, size, obstacles=[]):
    """Computes A* algorithm on weighted graph"""
    if source == target:
        return target
    m, n = size
    G = nx.grid_2d_graph(m+1, n+1)
    for obs, cost in obstacles:
        for obstacle in obs:
            if 0 <= obstacle.position[0] < m and 0 <= obstacle.position[1] < n:
                for neighbor_position in G[obstacle.position]:
                    G[obstacle.position][neighbor_position]['weight'] = cost
    path = nx.astar_path(G, source, target, manhattan)
    return path[1]
