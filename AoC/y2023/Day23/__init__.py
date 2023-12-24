import sys
import os.path
import uuid
from datetime import timedelta
from typing import Callable, AnyStr, Optional, Dict, List, Tuple, Iterable, Generator, Iterator, Set, Deque, Any, Type, \
    Union
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
from networkx.algorithms.dag import transitive_closure

from ..Day17 import tpl_add, tpl_mult, tpl_dist

# noinspection DuplicatedCode
DAY = int(os.path.basename(os.path.dirname(__file__))[3:])
YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[1:])

RENDER = True

SLOPES = {
    "<": (-1, 0),
    ">": (1, 0),
    "v": (0, 1),
    "^": (0, -1),
}


@Preprocessor(year=YEAR, day=DAY, task=1)
def preproc_1(data: List[str]):
    return preproc(data=data, normal_path=(".",), slopes=SLOPES)


@Preprocessor(year=YEAR, day=DAY, task=2)
def preproc_2(data: List[str]):
    return preproc(data=data, normal_path=(".", *SLOPES.keys()), slopes=dict())


def preproc(data: List[str], normal_path: Tuple[str, ...], slopes: Dict[str, Tuple[int, int]]):
    data = [x.strip() for x in data if len(x.strip()) > 0]
    slope_fields = set()
    g = nx.DiGraph()
    w, h = len(data[0]), len(data)
    if not all(len(x) == w for x in data):
        raise Exception()
    start, goal = None, None
    for y, line in enumerate(data):
        for x, c in enumerate(line):
            ns = []
            if c in normal_path:
                if start is None:
                    start = (x, y)
                goal = (x, y)
                for dx, dy in SLOPES.values():
                    ns.append((x + dx, y + dy))
            elif c in slopes:
                slope_fields.add((x, y))
                dx, dy = slopes[c]
                ns.append((x + dx, y + dy))
            elif c in ("#",):
                pass
            else:
                Exception()
            for n in ns:
                if 0 <= n[0] < w and 0 <= n[1] < h and data[n[1]][n[0]] in (*normal_path, *slopes.keys()):
                    g.add_edge((x, y), n)
    if start is None:
        raise Exception()
    return g, slope_fields, start, goal


@Task(year=YEAR, day=DAY, task=1, extra_config={"render": RENDER})
def task_01(
        data: Tuple[nx.DiGraph, Set[Tuple[int, int]], Tuple[int, int], Tuple[int, int]], log: Callable[[AnyStr], None],
        render: bool
):
    g, slope_fields, start, goal = data
    return task(
        g=g, start=start, goal=goal, log=log, slope_fields=slope_fields,
        render=os.path.join(os.path.dirname(__file__), "p1.png") if render else None
    )


@Task(year=YEAR, day=DAY, task=2, extra_config={"render": RENDER})
def task_02(
        data: Tuple[nx.DiGraph, Set[Tuple[int, int]], Tuple[int, int], Tuple[int, int]], log: Callable[[AnyStr], None],
        render: bool
):
    g, slope_fields, start, goal = data
    return task(
        g=g, start=start, goal=goal, log=log, slope_fields=slope_fields,
        render=os.path.join(os.path.dirname(__file__), "p2.png") if render else None
    )


def task(
        g: nx.DiGraph, start: Tuple[int, int], goal: Tuple[int, int], log: Callable[[AnyStr], None],
        slope_fields: Set[Tuple[int, int]], render: Optional[str] = None
) -> int:
    log(f"Getting longest path from {start} to {goal}")
    log(f"The Generated map has {len(g.nodes)} nodes and {len(g.edges)} edges")

    t1 = perf_counter()
    g2, steps = simplify_graph(g=g, start=start, goal=goal)
    t2 = perf_counter()
    log(f"Simplification took {timedelta(seconds=t2 - t1)}. It now has {len(g2.nodes)} nodes and {len(g2.edges)} edges")

    mi, ma, num_paths = None, None, 0
    desc = "Min: {mi}; Max: {ma}"
    with tqdm(nx.all_simple_paths(g2, start, goal), desc=desc.format(mi=mi, ma=ma), leave=False, unit="p") as pb:
        t1 = perf_counter()
        for path in pb:
            p_len = sum(len(steps[(n1, n2)]) + 1 for n1, n2 in zip(path, path[1:]))
            if mi is None or p_len < mi[0]:
                mi = p_len, path
            if ma is None or p_len > ma[0]:
                ma = p_len, path
            pb.set_description(desc.format(mi=mi[0], ma=ma[0]))
            num_paths += 1
        t2 = perf_counter()
    log(f"Checking {num_paths} paths took {timedelta(seconds=t2 - t1)}. {(t2 - t1) / num_paths:.10f}s per path")
    log(f"{num_paths} path would bring you to your goal. The longest is {ma[0]} steps vs the shortest {mi[0]} steps")

    if render is not None:
        from PIL import Image, ImageDraw

        max_path, min_path = set(), set()
        for n1, n2 in zip(ma[1], ma[1][1:]):
            max_path.update((n1, n2), steps[n1, n2])
        for n1, n2 in zip(mi[1], mi[1][1:]):
            min_path.update((n1, n2), steps[n1, n2])

        w = max(x[0] for x in g.nodes) - min(x[0] for x in g.nodes)
        h = max(x[1] for x in g.nodes) - min(x[1] for x in g.nodes)

        pixel_size = 10
        offset = ceil(pixel_size * 1.5)

        bg = (0, 0, 0)
        rock = (127, 131, 134)
        path = (118, 85, 43)
        symbols = (234, 208, 168)
        ice = (186, 242, 239)

        img = Image.new("RGB", (offset * 2 + w * pixel_size, offset * 2 + h * pixel_size), bg)
        draw = ImageDraw.Draw(img)

        for x in range(-1, w + 1, 1):
            for y in range(-1, h + 1, 1):
                xc, yc = x * pixel_size + offset, y * pixel_size + offset
                xcc, ycc = xc + pixel_size, yc + pixel_size
                if (x, y) in g:
                    draw.rectangle(xy=((xc, yc), (xcc, ycc)),
                                   fill=ice if (x, y) in slope_fields else path,
                                   outline=ice if (x, y) in slope_fields else path, width=1)
                    if (x, y) in max_path:
                        draw.ellipse(xy=((xc, yc), (xcc, ycc)), fill=None, outline=symbols, width=ceil(pixel_size / 10))
                    if (x, y) in min_path:
                        draw.line(xy=((xc, yc), (xcc, ycc)), fill=symbols, width=ceil(pixel_size / 10))
                        draw.line(xy=((xc, ycc), (xcc, yc)), fill=symbols, width=ceil(pixel_size / 10))
                else:
                    draw.rectangle(xy=((xc, yc), (xcc, ycc)), fill=rock, outline=rock, width=1)

        img.save(render)
        log(f"Saved rendered image to {render}")

    return ma[0]


def simplify_graph(g: nx.DiGraph, start: Tuple[int, int], goal: Tuple[int, int]):
    g: nx.DiGraph = g.copy(False)
    # dist: Dict[Tuple[Tuple[int, int], Tuple[int, int]], int] = defaultdict(lambda: 1)
    steps_between: Dict[Tuple[Tuple[int, int], Tuple[int, int]], List[Tuple[int, int]]] = defaultdict(lambda: [])

    one_found = True

    while one_found:
        one_found = False
        for n in sorted(g.nodes):
            if n not in (start, goal) and len(g[n]) == 2:
                c1, c2 = g[n]
                if g.has_edge(c1, n) and g.has_edge(n, c2) and g.has_edge(c2, n) and g.has_edge(n, c1):
                    # new_dist = dist[(c1, n)] + dist[(n, c2)]
                    g.add_edge(c1, c2)
                    g.add_edge(c2, c1)
                    # dist[(c1, c2)] = new_dist
                    # dist[(c2, c1)] = new_dist
                    steps_between[(c1, c2)] = steps_between[(c1, n)] + [n] + steps_between[(n, c2)]
                    steps_between[(c2, c1)] = steps_between[(c2, n)] + [n] + steps_between[(n, c1)]
                    # if new_dist != len(steps_between[(c1, c2)]) + 1 or new_dist != len(steps_between[(c2, c1)]) + 1:
                    # raise Exception()
                    g.remove_node(n)
                    one_found = True
                    break

    return g, steps_between
