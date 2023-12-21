import sys
import os.path
from datetime import timedelta
from typing import Callable, AnyStr, Optional, Dict, List, Tuple, Iterable, Generator, Iterator, Set, Deque, Any, Type
from collections import defaultdict, OrderedDict, Counter
from time import perf_counter
from itertools import chain
from functools import lru_cache
from copy import deepcopy
from math import lcm, ceil, floor, prod
import re
from queue import PriorityQueue, Queue
from operator import xor
from abc import ABC, abstractmethod
from enum import Enum
from pprint import pformat, pprint

import matplotlib.pyplot as plt
from shapely import Polygon, Point, LineString
from tqdm import tqdm, trange
import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor
import networkx as nx
import graphblas_algorithms as ga
from networkx.drawing.nx_pydot import graphviz_layout
from scipy.interpolate import KroghInterpolator, BarycentricInterpolator, lagrange

from ..Day17 import tpl_add, tpl_mult, tpl_dist

# noinspection DuplicatedCode
DAY = int(os.path.basename(os.path.dirname(__file__))[3:])
YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[1:])

RENDER = True


@Preprocessor(year=YEAR, day=DAY)
def preproc_1(data: List[str]):
    data = [x.strip() for x in data if len(x.strip()) > 0]
    if sum(1 if c == "S" else 0 for c in chain(*data)) != 1:
        raise Exception()
    w, h = len(data[0]), len(data)
    if any(len(x) != w for x in data):
        raise Exception()
    g = nx.Graph()
    start = None
    for y, line in enumerate(data):
        for x, c in enumerate(line):
            if c == "#":
                continue
            elif c in (".", "S"):
                p1 = (x, y)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    p2 = (x + dx, y + dy)
                    if 0 <= p2[0] < w and 0 <= p2[1] < h:
                        if data[p2[1]][p2[0]] in (".", "S"):
                            g.add_edge(p1, p2)
                if c == "S":
                    start = p1
            else:
                raise Exception()

    return g, start, (w, h)


@Preprocessor(year=YEAR, day=DAY, task=2)
def preproc_2(data: Tuple[nx.Graph, Tuple[int, int], Tuple[int, int]]) -> Tuple[nx.Graph, Tuple[int, int], Tuple[int, int]]:
    g, start, (w, h) = data

    for x in range(w):
        p1, p2 = (x, 0), (x, h - 1)
        if p1 in g and p2 in g:
            g.add_edge(p1, p2)
            g.add_edge(p2, p1)

    for y in range(h):
        p1, p2 = (0, y), (w - 1, y)
        if p1 in g and p2 in g:
            g.add_edge(p1, p2)
            g.add_edge(p2, p1)

    return g, start, (w, h)


@Task(year=YEAR, day=DAY, task=1, extra_config={"step_count": 64})
def task_01(data: Tuple[nx.Graph, Tuple[int, int], Tuple[int, int]], log: Callable[[AnyStr], None], step_count: int):
    g, start, (w, h) = data
    return num_reachable_plots(g=g, size=(w, h), start=start, step_count=step_count, log=log)


@Task(year=YEAR, day=DAY, task=2, extra_config={"step_count": 26501365})
def task_02(data: Tuple[nx.Graph, Tuple[int, int], Tuple[int, int]], log: Callable[[AnyStr], None], step_count: int):
    g, start, (w, h) = data
    return num_reachable_plots(g=g, size=(w, h), start=start, step_count=step_count, log=log)


def num_reachable_plots(
        g: nx.Graph, size: Tuple[int, int], start: Tuple[int, int], step_count: int, log: Callable[[AnyStr], None]
) -> int:
    w, h = size
    if step_count < min(size) and False:
        log(f"Field has a size of {w}x{h} and you stay in it")
        # Easy way
        log(f"You want to do {step_count} steps")
        t1 = perf_counter()
        # node_distances = nx.single_source_shortest_path_length(ga.Graph.from_networkx(g), start)
        node_distances = nx.single_source_shortest_path_length(g, start)
        t2 = perf_counter()
        log(f"Distance calculation took {t2 - t1:.6f}s")
        exp_mod = step_count % 2
        filtered_nodes = [n for n, d in node_distances.items() if d <= step_count and d % 2 == exp_mod]
        return len(filtered_nodes)

    log(f"Field has a size of {w}x{h}. Start is at {start}. Graph has {len(g.nodes)} nodes and {len(g.edges)} edges")
    log(f"You want to do {step_count} steps")

    poly_possible = w == h and all(floor(k/2) <= s <= ceil(k/2) for s, k in zip(start, size))

    log(f"Polynomial interpolation is {'' if poly_possible else 'not '}possible")

    visited = set()
    new_reachable: List[Tuple[int, int]] = [(0, 1)]
    wave_front: Set[Tuple[int, ...]] = set()
    wave_front.add(start)

    i = trange(step_count + 1, leave=False, total=step_count, desc="Step") if step_count > min(w, h) else range(step_count + 1)

    for step in i:

        if step >= step_count:
            break

        # step += 1

        new_wavefront = set()

        while wave_front:
            p = wave_front.pop()
            pc = move_tpl(t1=p, size=(w, h))
            nexts = list(g[pc])
            visited.add(p)
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = tpl_add(t1=p, t2=d)
                if n in visited:
                    continue
                nc = move_tpl(t1=n, size=(w, h))
                if nc not in nexts:
                    continue
                new_wavefront.add(n)

        reachable = len(new_wavefront)
        new_reachable.append((step, reachable))

        wave_front = new_wavefront

        if poly_possible and step >= 3 * w:
            log("Too many steps done. Will try polynomial interpolation")
            break

    if len(new_reachable) < step_count:
        x = [w//2 + i * w for i in range(3)]
        y = [sum((x[1] for x in new_reachable[:s+1][::-2])) for s in x]
        log(f"Polynomial interpolation using {', '.join(f'({x1},{y1})' for x1, y1 in zip(x, y))}")
        poly = lagrange(list(range(len(x))), y)
        return poly((step_count - w//2)/131)

    return sum((x[1] for x in new_reachable[:step_count+1][::-2]))


def move_tpl(t1: Tuple[int, ...], size: Tuple[int, ...]) -> Tuple[int, ...]:
    return tuple(x % c for x, c in zip(t1, size))
