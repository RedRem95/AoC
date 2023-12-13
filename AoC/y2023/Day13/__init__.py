import sys
import os.path
from datetime import timedelta
from typing import Callable, AnyStr, Optional, Dict, List, Tuple, Iterable, Generator, Iterator, Set
from collections import defaultdict
from time import perf_counter
from itertools import chain
from functools import lru_cache
from copy import deepcopy
from math import lcm, ceil
import re

from shapely import Polygon, Point
from tqdm import tqdm
import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

# noinspection DuplicatedCode
DAY = int(os.path.basename(os.path.dirname(__file__))[3:])
YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[1:])


@Preprocessor(year=YEAR, day=DAY)
def preproc_1(data: List[str]) -> List[np.ndarray]:
    data = [x.strip() for x in data]
    n = 0
    while len(data[n]) <= 0:
        n += 1
    ret = []
    current: List[List[bool]] = []
    for line in data[n:]:
        if len(line) <= 0:
            if len(current) > 0:
                ret.append(np.array(current))
            current = []
        else:
            if any(x not in ("#", ".") for x in line):
                raise Exception()
            current.append([True if x == "#" else False for x in line])
    if len(current) > 0:
        ret.append(np.array(current))
    return ret


def is_mirror(check_map: np.ndarray, row: int, smudge_correction: bool = False) -> bool:
    if not (0 <= row < check_map.shape[0] - 1):
        return False
    s = 0
    ru, rl = row, row + 1
    while 0 <= ru and rl < check_map.shape[0]:
        s += check_map.shape[1] - np.sum(check_map[ru, :] == check_map[rl, :])
        ru -= 1
        rl += 1
    return s == (1 if smudge_correction else 0)


def find_mirror_axis(check_map: np.ndarray, smudge_correction: bool = False) -> Tuple[Optional[str], int]:
    h_map = check_map
    v_map = check_map.transpose()

    center_h = ceil(h_map.shape[0] / 2)
    center_v = ceil(v_map.shape[0] / 2)

    i = 0
    while i <= max(center_v, center_h):
        for m, o, r in [(h_map, "H", center_h + i), (h_map, "H", center_h - i), (v_map, "V", center_v + i), (v_map, "V", center_v - i)]:
            if is_mirror(check_map=m, row=r, smudge_correction=smudge_correction):
                return o, r
        i += 1
    return None, -1


@Task(year=YEAR, day=DAY, task=1)
def task_01(data: List[np.ndarray], log: Callable[[AnyStr], None]):
    return task(data=data, log=log, smudge_correction=False)


@Task(year=YEAR, day=DAY, task=2)
def task_01(data: List[np.ndarray], log: Callable[[AnyStr], None]):
    return task(data=data, log=log, smudge_correction=True)


def task(data: List[np.ndarray], log: Callable[[AnyStr], None], smudge_correction: bool):
    log(f"Checking {len(data)} maps {'with' if smudge_correction else 'without'} the smudge correction")
    mirror_axis = {"H": [], "V": []}
    for o, r in (find_mirror_axis(check_map=m, smudge_correction=smudge_correction) for m in data):
        mirror_axis[o].append(r)
    h_axis = sum((x + 1 for x in mirror_axis["H"]))
    v_axis = sum((x + 1 for x in mirror_axis["V"]))
    log(f"Sum of horizontal mirror axis: {h_axis}; Sum of vertical mirror axis: {v_axis}")
    ret = 100 * h_axis + v_axis
    return ret
