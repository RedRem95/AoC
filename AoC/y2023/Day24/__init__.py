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


@Preprocessor(year=YEAR, day=DAY)
def preproc_1(data: List[str]) -> List[Tuple[Tuple[int, int, int], Tuple[int, int, int]]]:
    ret: List[Tuple[Tuple[int, int, int], Tuple[int, int, int]]] = []
    for line in (x.strip() for x in data if len(x.strip()) > 0):
        p, v = line.split("@")
        px, py, pz = p.split(",")
        vx, vy, vz = v.split(",")
        ret.append(((int(px), int(py), int(pz)), (int(vx), int(vy), int(vz))))
    return ret


@Task(year=YEAR, day=DAY, task=1)
def task_01(data: List[Tuple[Tuple[int, int, int], Tuple[int, int, int]]], log: Callable[[AnyStr], None]):
    log(f"Checking {len(data)} hails")
    x_min, x_max, y_min, y_max = 200000000000000, 400000000000000, 200000000000000, 400000000000000
    # x_min, x_max, y_min, y_max = 7, 27, 7, 27

    intersections = []

    for i, ((px1, py1, _), (vx1, vy1, _)) in enumerate(data):
        i: int
        p11, p12 = (px1, py1), tpl_add((px1, py1), (vx1, vy1))
        for j, ((px2, py2, _), (vx2, vy2, _)) in enumerate(data[i + 1:], i + 1):
            p21, p22 = (px2, py2), tpl_add((px2, py2), (vx2, vy2))
            intersection = line_intersection((p11, p12), (p21, p22))
            if intersection is not None and x_min <= intersection[0] <= x_max and y_min <= intersection[1] <= y_max:
                ix, iy = intersection
                if all(_ >= 0 for _ in ((ix - px1) / vx1, (iy - py1) / vy1, (ix - px2) / vx2, (iy - py2) / vy2)):
                    intersections.append((i, j, intersection))

    ret = len(intersections)

    log(f"There are {ret} intersections of hail trajectories in the future")

    return ret


@Task(year=YEAR, day=DAY, task=2)
def task_02(data: List[Tuple[Tuple[int, int, int], Tuple[int, int, int]]], log: Callable[[AnyStr], None]):

    from z3.z3 import Int, Real, Solver, sat

    p_target = Int('x'), Int('y'), Int('z')
    v_target = Int('vx'), Int('vy'), Int('vz')

    solver = Solver()

    for i, (ph, vh) in enumerate(data):

        t = Int(f"t_{i}")
        for j in range(len(p_target)):
            solver.add(p_target[j] + v_target[j] * t == ph[j] + vh[j] * t)

    log(f"Solver says: {'good to go' if solver.check() == sat else 'uff, not good'}")

    model = solver.model()
    p_results = [model.evaluate(x).as_long() for x in p_target]
    v_results = [model.evaluate(x).as_long() for x in v_target]

    log(f"Solver says you have to stand at {p_results} and throw in direction {v_results}")

    return sum(p_results)


def line_intersection(line1: Tuple[Tuple[int, int], Tuple[int, int]], line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return None

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y
