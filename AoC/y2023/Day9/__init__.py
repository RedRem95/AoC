from typing import Callable, AnyStr, Optional, Dict, List, Tuple, Iterable, Generator, Iterator, Set
from collections import defaultdict
from time import perf_counter
from itertools import chain
from functools import lru_cache
from copy import deepcopy
from math import lcm

from tqdm import tqdm
import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2023, day=9)
def preproc_1(data: List[str]) -> List[List[int]]:
    ret = []
    for line in (x.strip() for x in data if len(x.strip()) > 0):
        ret.append([])
        for n in (x.strip() for x in line.split(" ") if len(x.strip()) > 0):
            ret[-1].append(int(n))
    return ret


def extrapolate(data_line: List[int]) -> List[List[int]]:
    r = [[x for x in data_line]]
    while not all(x == 0 for x in r[-1]):
        r.append([x2 - x1 for x1, x2 in zip(r[-1], r[-1][1:])])
        if len(r[-1]) <= 0:
            raise Exception()
    r[-1].append(0)
    r[-1].insert(0, 0)
    for i in range(len(r) - 2, -1, -1):
        r[i].append(r[i+1][-1] + r[i][-1])
        r[i].insert(0, r[i][0] - r[i+1][0])
    return r


@Task(year=2023, day=9, task=1)
def task01(data: List[List[int]], log: Callable[[AnyStr], None]):
    log(f"Processing {len(data)} datalines")
    log(f"Max dataline length: {max(len(x) for x in data)}")
    produced_histories = [extrapolate(data_line=x) for x in data]
    log(f"Max extrapolated history length: {max(len(x) for x in produced_histories)}")
    ret = sum(x[0][-1] for x in produced_histories)
    log(f"Sum of all extrapolated last history values: {ret}")
    return ret


@Task(year=2023, day=9, task=2)
def task02(data: List[List[int]], log: Callable[[AnyStr], None]):
    log(f"Processing {len(data)} datalines")
    log(f"Max dataline length: {max(len(x) for x in data)}")
    produced_histories = [extrapolate(data_line=x) for x in data]
    log(f"Max extrapolated history length: {max(len(x) for x in produced_histories)}")
    ret = sum(x[0][0] for x in produced_histories)
    log(f"Sum of all extrapolated first history values: {ret}")
    return ret
