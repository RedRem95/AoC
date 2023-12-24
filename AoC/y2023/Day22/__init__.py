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

from ..Day17 import tpl_add, tpl_mult, tpl_dist

# noinspection DuplicatedCode
DAY = int(os.path.basename(os.path.dirname(__file__))[3:])
YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[1:])

RENDER = True


@Preprocessor(year=YEAR, day=DAY)
def preproc_1(data: List[str]):
    bricks = []
    for line in (x.strip() for x in data if len(x.strip()) > 0):
        p1, p2 = line.split("~")
        b = Brick(p1=tuple(int(x) for x in p1.split(",")), p2=tuple(int(x) for x in p2.split(",")))
        bricks.append(b)
    return bricks


@Task(year=YEAR, day=DAY, task=1)
def task_01(data: List["Brick"], log: Callable[[AnyStr], None]):
    resting_cubes = lay_bricks(bricks=data, log=log)

    important_supports = set()

    for b in resting_cubes:
        if b.num_supporting_cubes == 1:
            important_supports.update(b.iter_rests_on())

    log(f"{len(important_supports)} ({100 * len(important_supports) / len(data):.2f}%) bricks are structural")

    return len(data) - len(important_supports)


@Task(year=YEAR, day=DAY, task=2)
def task_02(data: List["Brick"], log: Callable[[AnyStr], None]):
    resting_cubes = lay_bricks(bricks=data, log=log)
    chained_fall: Dict[Brick, int] = defaultdict(lambda: 0)

    for i, b in enumerate(resting_cubes):
        is_falling = set()
        is_falling.add(b)

        for b2 in resting_cubes[i+1:]:
            rests_on_bricks = set(b2.iter_rests_on())
            rests_on_bricks.difference_update(is_falling)
            if not Brick.check_resting(brick=b2, rests_on=rests_on_bricks):
                is_falling.add(b2)

        chained_fall[b] = len(is_falling) - 1

    chained_fall_sorted = sorted([(x, y) for x, y in chained_fall.items()], key=lambda x: -x[1])

    log(f"The biggest chain reaction can be created by disintegrating {chained_fall_sorted[0][0]} "
        f"which makes {chained_fall_sorted[0][1]} "
        f"({100 * chained_fall_sorted[0][1] / len(data):.2f}%) bricks fall down. Insane")

    return sum(x[1] for x in chained_fall_sorted)


def lay_bricks(bricks: List["Brick"], log: Callable[[AnyStr], None]) -> List["Brick"]:
    log(f"Simulating {len(bricks)} bricks")
    resting_cubes: Dict[int, List[Brick]] = defaultdict(lambda: [])
    t1 = perf_counter()
    bricks = sorted(bricks, key=Brick.compare_key)
    for b in bricks:
        while not b.is_resting:
            for ob in resting_cubes[b.lower_bound - 1]:
            # for ob in chain(*resting_cubes.values()) :
                b.rests_on(other=ob)
            b.move_down(n=1)
        resting_cubes[b.upper_bound].append(b)
    t2 = perf_counter()
    log(f"Simulation took {timedelta(seconds=t2 - t1)}")
    return bricks


def id_to_ab(idx: int) -> str:
    last = idx % 26
    rest = idx // 26
    return f"{'' if rest <= 0 else id_to_ab(idx=rest-1)}{chr(ord('A') + last)}"


class Brick(object):
    _ID = [0]

    def __init__(self, p1: Tuple[int, ...], p2: Tuple[int, ...]):
        if any(len(x) != 3 for x in (p1, p2)):
            raise Exception()
        self._id = id_to_ab(self.__class__._ID[0])
        self.__class__._ID[0] += 1
        # noinspection PyTypeChecker
        self._p1: Tuple[int, int, int] = p1
        # noinspection PyTypeChecker
        self._p2: Tuple[int, int, int] = p2

        self._min_x, self._max_x = min(x[0] for x in (p1, p2)), max(x[0] for x in (p1, p2))
        self._min_y, self._max_y = min(x[1] for x in (p1, p2)), max(x[1] for x in (p1, p2))

        self._corners: Optional[Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]] = (
            (self._min_x, self._min_y),
            (self._max_x, self._min_y),
            (self._max_x, self._max_y),
            (self._min_x, self._max_y)
        )

        self._layer: Tuple[Tuple[int, int]] = tuple()

        for x in range(self._min_x, self._max_x + 1, 1):
            for y in range(self._min_y, self._max_y + 1, 1):
                self._layer += ((x, y),)

        self._rests_on = []

    def get_outer_bounds(self) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        return (
            (self._min_x, self._min_y, self.lower_bound),
            (self._max_x, self._max_y, self.upper_bound)
        )

    def move_down(self, n: int=1) -> bool:
        if self.is_resting:
            return False
        self._p1 = tpl_add(t1=self._p1, t2=(0, 0, -n))
        self._p2 = tpl_add(t1=self._p2, t2=(0, 0, -n))
        return True

    def get_cubes(self, d3: bool = False):
        if d3:
            raise NotImplementedError()
        return self._layer

    @property
    def upper_bound(self):
        return max(x[2] for x in (self._p1, self._p2))

    @property
    def lower_bound(self):
        return min(x[2] for x in (self._p1, self._p2))

    @property
    def num_supporting_cubes(self) -> int:
        return len(self._rests_on)

    @staticmethod
    def compare_key(brick: "Brick"):
        return min(x[2] for x in (brick._p1, brick._p2))

    @property
    def is_resting(self) -> bool:
        return self.check_resting(self, self._rests_on)

    @staticmethod
    def check_resting(brick: "Brick", rests_on: Union[List["Brick"], Set["Brick"]] = None):
        if rests_on is None:
            rests_on = brick._rests_on
        return len(rests_on) > 0 or any(x[2] == 1 for x in (brick._p1, brick._p2))

    def iter_rests_on(self) -> Iterator["Brick"]:
        return iter(self._rests_on)

    def __eq__(self, other: "Brick"):
        if not isinstance(other, self.__class__):
            raise Exception()
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)

    def _check_intersects(self, other: "Brick"):
        own_layer, other_layer = self.get_cubes(), other.get_cubes()
        return any(x in own_layer for x in other_layer)

    def rests_on(self, other: "Brick") -> bool:
        if not other.is_resting:
            return False
        if max(other._p1[2], other._p2[2]) == min(self._p1[2], self._p2[2]) - 1 and self._check_intersects(other=other):
            self._rests_on.append(other)
            return True
        return False

    def __repr__(self):
        return (f"<{self.__class__.__name__}: {self._id}, "
                f"p1 {self._p1}, p2 {self._p2}, resting {self.is_resting}, {self.num_supporting_cubes}>")

    def __str__(self):
        ob = self.get_outer_bounds()
        return f"{self.__class__.__name__} {self._id} @ {ob[0]}x{ob[1]}"
