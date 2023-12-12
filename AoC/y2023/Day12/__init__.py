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


DAY = int(os.path.basename(os.path.dirname(__file__))[3:])
YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[1:])


@Preprocessor(year=YEAR, day=DAY)
def preproc_1(data: List[str]) -> List[Tuple[str, List[int]]]:
    ret = []
    for line in (x.strip() for x in data if len(x.strip()) > 0):
        springs, condition = line.split(" ")
        if any(x not in (".", "#", "?") for x in springs):
            raise Exception()
        ret.append((springs, [int(x) for x in condition.split(",")]))
    return ret


@lru_cache(maxsize=None)
def _count_down(t: Tuple[int, ...]):
    return t[0] - 1, *t[1:]


@lru_cache(maxsize=None)
def _process_line_rec(springs: str, condition: Tuple[int, ...], last_was_defect: bool) -> int:
    if len(condition) <= 0:  # All conditions are met
        if "#" in springs:  # There should not be a defect left
            return 0
        else:
            return 1
    if len(springs) <= 0:  # All input data has been processed
        if sum(condition) > 0:  # All conditions should be met by now
            return 0
        else:
            return 1
    if condition[0] == 0:  # If current condition over
        if springs[0] in ("?", "."):  # Next needs to be a non defect, then continue
            return _process_line_rec(springs=springs[1:], condition=condition[1:], last_was_defect=False)
        else:
            return 0
    if last_was_defect:  # Last was defect but current condition cant be over (see above)
        if springs[0] in ("?", "#"):
            return _process_line_rec(springs=springs[1:], condition=_count_down(condition), last_was_defect=True)
        else:
            return 0
    r = 0
    if springs[0] in ("#", "?"):  # Current one is a defect
        r += _process_line_rec(springs=springs[1:], condition=_count_down(condition), last_was_defect=True)
    if springs[0] in (".", "?"):  # Current one is working
        r += _process_line_rec(springs=springs[1:], condition=condition, last_was_defect=False)
    return r


@Task(year=YEAR, day=DAY, task=1)
def task_01(data: List[Tuple[str, List[int]]], log: Callable[[AnyStr], None]):
    return task(data=data, log=log)


@Task(year=YEAR, day=DAY, task=2, extra_config={"cnt": 5})
def task_02(data: List[Tuple[str, List[int]]], log: Callable[[AnyStr], None], cnt: int):
    return task(data=[("?".join(s for _ in range(cnt)), p * cnt) for s, p in data], log=log)


def task(data: List[Tuple[str, List[int]]], log: Callable[[AnyStr], None]):
    data = [(x[0], tuple(x[1])) for x in data]
    log(f"checking {len(data)} condition records")
    log(f"Maximum length of springs is {max(len(x) for x, _ in data)}")
    total_permutations = [2 ** sum(y == "?" for y in x) for x, _ in data]
    log(f"Total number of permutations in all records: {sum(total_permutations)}")
    ret = sum(_process_line_rec(springs=s, condition=c, last_was_defect=False) for s, c in data)
    log(f"{ret} spring permutations match the condition")
    return ret
