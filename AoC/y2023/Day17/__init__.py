import sys
import os.path
from datetime import timedelta
from typing import Callable, AnyStr, Optional, Dict, List, Tuple, Iterable, Generator, Iterator, Set, Deque
from collections import defaultdict, OrderedDict
from time import perf_counter
from itertools import chain
from functools import lru_cache
from copy import deepcopy
from math import lcm, ceil
import re
from queue import PriorityQueue

from shapely import Polygon, Point
from tqdm import tqdm
import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

from ..Day16 import tpl_add

# noinspection DuplicatedCode
DAY = int(os.path.basename(os.path.dirname(__file__))[3:])
YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[1:])

RENDER = True


@Preprocessor(year=YEAR, day=DAY)
def preproc_1(data: List[str]) -> np.ndarray:
    tmp = [[int(y) for y in x.strip()] for x in data if len(x.strip()) > 0]
    return np.array(tmp)


@Task(year=YEAR, day=DAY, task=1, extra_config={"render": RENDER})
def task_01(data: np.ndarray, log: Callable[[AnyStr], None], render: bool):
    return task(
        data=data, log=log, min_steps=1, max_steps=3,
        render_name=os.path.join(os.path.dirname(__file__), "p1.png") if render else None
    )


@Task(year=YEAR, day=DAY, task=2, extra_config={"render": RENDER})
def task_02(data: np.ndarray, log: Callable[[AnyStr], None], render: bool):
    return task(
        data=data, log=log, min_steps=4, max_steps=10,
        render_name=os.path.join(os.path.dirname(__file__), "p2.png") if render else None
    )


def task(data: np.ndarray, log: Callable[[AnyStr], None], min_steps, max_steps, render_name: Optional[str]):
    h, w = data.shape
    start_point = 0, 0
    end_point = h-1, w-1
    log(f"Factory city has a size of {w}x{h}")
    ret, path = path_search(city_map=data, start=start_point, end=end_point, min_steps=min_steps, max_steps=max_steps)
    log(f"The minimum heat loss you can take is {ret}")
    if render_name:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 1)
        fig: plt.Figure
        ax: plt.Axes
        fig.set_size_inches(20, 20)
        fig.set_dpi(600)
        cbar = ax.imshow(data, cmap="RdYlBu")
        ax.plot([x[1] for x in path], [x[0] for x in path], color="black")
        fig.colorbar(cbar, ax=ax)
        fig.savefig(render_name)
    return ret


def tpl_dist(t1: Tuple[int, ...], t2: Tuple[int, ...]) -> int:
    return sum(abs(i - j) for i, j in zip(t1, t2))


def tpl_mult(t1: Tuple[int, ...], mult: int) -> Tuple[int, ...]:
    return tuple(x * mult for x in t1)


def check_out_bounds(tpl: Tuple[int, ...], area: Tuple[int, ...]):
    return any(not (0 <= i < j) for i, j in zip(tpl, area))


def path_search(
        city_map: np.ndarray, start: Tuple[int, int], end: Tuple[int, int], min_steps: int, max_steps: int,
) -> Tuple[int, List[Tuple[int, int]]]:

    current: PriorityQueue[Tuple[int, int, Tuple[int, int], Tuple[int, int], List[Tuple[int, int]]]] = PriorityQueue()
    current.put((0, 0, start, (0, 0), [start]))
    visited: Dict[Tuple[Tuple[int, int], Tuple[int, int]], int] = {}
    i = 0
    while current:
        i += 1
        current_heat, _, current_position, current_direction, path = current.get()
        if current_position == end:
            return current_heat, path
        if visited.get((current_position, current_direction), np.inf) <= current_heat:
        # if (current_position, current_direction) in visited:
            continue
        visited[(current_position, current_direction)] = current_heat
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if d in (current_direction, tpl_mult(current_direction, -1)):
                continue
            new_position = current_position
            new_heat = current_heat
            for step in range(1, max_steps + 1, 1):
                new_position = tpl_add(new_position, d)
                if not check_out_bounds(new_position, city_map.shape):
                    new_heat += city_map[new_position]
                    if step >= min_steps:
                        current.put((new_heat, tpl_dist(new_position, end), new_position, d, path + [new_position]))
    return -1, []
