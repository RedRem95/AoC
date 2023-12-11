import os.path
from datetime import timedelta
from typing import Callable, AnyStr, Optional, Dict, List, Tuple, Iterable, Generator, Iterator, Set
from collections import defaultdict
from time import perf_counter
from itertools import chain
from functools import lru_cache
from copy import deepcopy
from math import lcm, ceil

from shapely import Polygon, Point
from tqdm import tqdm
import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


DAY = 11


@Preprocessor(year=2023, day=DAY, task=1)
def preproc_1(data: List[str]) -> List[Tuple[int, int]]:
    return preproc(data=data, expansion=1)


@Preprocessor(year=2023, day=DAY, task=2)
def preproc_1(data: List[str]) -> List[Tuple[int, int]]:
    return preproc(data=data, expansion=999999)


def preproc(data: List[str], expansion: int) -> List[Tuple[int, int]]:
    data = [x.strip() for x in data if len(x.strip()) > 0]
    if not all(len(x) == len(data[0]) for x in data):
        raise Exception()
    ret: List[Tuple[int, int]] = []

    tmp: List[List[str]] = [[y for y in x] for x in data]

    for i, line in enumerate(tmp):
        for j, c in enumerate(line):
            if c == ".":
                continue
            elif c == "#":
                ret.append((i, j))
            else:
                raise Exception(f"{c} could not be processed")

    for i in range(len(tmp) - 1, -1, -1):
        if all(x == "." for x in tmp[i]):
            for j in range(len(ret)):
                if ret[j][0] > i:
                    ret[j] = (ret[j][0] + expansion, ret[j][1])

    for i in range(len(tmp[0]) - 1, -1, -1):
        if all(tmp[j][i] == "." for j in range(len(tmp))):
            for j in range(len(ret)):
                if ret[j][1] > i:
                    ret[j] = (ret[j][0], ret[j][1] + expansion)

    return ret


def _dist(p1: Tuple[int, int], p2: Tuple[int, int]) -> int:
    return abs(p1[0]-p2[0]) + abs(p1[1] - p2[1])


@Task(year=2023, day=DAY, task=1)
def task_01(data: List[Tuple[int, int]], log: Callable[[AnyStr], None]):
    return task(data=data, log=log)


@Task(year=2023, day=DAY, task=2)
def task_02(data: List[Tuple[int, int]], log: Callable[[AnyStr], None]):
    return task(data=data, log=log)


def task(data: List[Tuple[int, int]], log: Callable[[AnyStr], None]):
    pairs = ((i, j) for i in range(len(data)) for j in range(i, len(data)))
    log(f"There are {len(data)} galaxies")
    amount_pairs = (len(data)**2 + len(data)) // 2
    log(f"Calculating the distance between {amount_pairs} galaxy pairs")
    dists = [_dist(data[x1], data[x2]) for x1, x2 in pairs]
    r = sum(dists)
    log(f"Max distance: {max(dists)}; Min distance: {min(dists)}; Sum of distances: {r}")
    print(data[4], data[8], _dist(data[4], data[5]))
    return r
