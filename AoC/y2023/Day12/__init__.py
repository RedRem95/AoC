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


def _sizeof_fmt(num, suffix="B", divisor: float = 1024.0):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < divisor:
            return f"{num:3.1f}{unit}{suffix}"
        num /= divisor
    return f"{num:.1f}Yi{suffix}"


def _get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([_get_size(v, seen) for v in obj.values()])
        size += sum([_get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += _get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([_get_size(i, seen) for i in obj])
    return size


def _get_size_fmt(obj):
    return _sizeof_fmt(_get_size(obj=obj))


DAY = int(os.path.basename(os.path.dirname(__file__))[3:])
YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[1:])


INSPECT_CACHE: bool = False
_CACHES: Dict[str, Dict] = {}


def _clear_cache():
    for c in _CACHES.values():
        c.clear()


def my_cache(func: Callable) -> Callable:
    i = 0
    fun_name = None
    while fun_name is None or fun_name in _CACHES:
        fun_name = f"{func.__name__}{f'_{i}' if i > 0 else ''}"
        i += 1
    _CACHES[fun_name] = {}

    def wrapper(*args, **kwargs):
        k = (*args, *sorted(kwargs.items()))
        if k not in _CACHES[fun_name]:
            _CACHES[fun_name][k] = func(*args, **kwargs)
        return _CACHES[fun_name][k]
    return wrapper


_cache_decorator = my_cache if INSPECT_CACHE else lru_cache(maxsize=None)


@Preprocessor(year=YEAR, day=DAY)
def preproc_1(data: List[str]) -> List[Tuple[str, List[int]]]:
    ret = []
    for line in (x.strip() for x in data if len(x.strip()) > 0):
        springs, condition = line.split(" ")
        if any(x not in (".", "#", "?") for x in springs):
            raise Exception()
        ret.append((springs, [int(x) for x in condition.split(",")]))
    return ret


@_cache_decorator
def _count_down(t: Tuple[int, ...]):
    return t[0] - 1, *t[1:]


@_cache_decorator
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
    t1 = perf_counter()
    data = [("?".join(s for _ in range(cnt)), p * cnt) for s, p in data]
    t2 = perf_counter()
    log(f"Repeating spring map and conditions {cnt} times took {timedelta(seconds=t2-t1)}")
    return task(data=data, log=log)


def task(data: List[Tuple[str, List[int]]], log: Callable[[AnyStr], None]):
    _clear_cache()
    data = [(x[0], tuple(x[1])) for x in data]
    log(f"checking {len(data)} condition records")
    log(f"Maximum length of springs is {max(len(x) for x, _ in data)}")
    total_permutations = [2 ** sum(y == "?" for y in x) for x, _ in data]
    log(f"Total number of permutations in all records: {sum(total_permutations)}")
    t1 = perf_counter()
    ret = sum(_process_line_rec(springs=s, condition=c, last_was_defect=False) for s, c in data)
    t2 = perf_counter()
    log(f"Processing {len(data)} records took {timedelta(seconds=t2-t1)}")
    log(f"{ret} spring permutations match the condition")
    if INSPECT_CACHE:
        log(f"Final cache sizes {_get_size_fmt(_CACHES)} "
            f"({', '.join(f'{k}: {_get_size_fmt(v)}' for k, v in _CACHES.items())})")
        log(f"Final elements in cache: {sum(len(x) for x in _CACHES.values())} "
            f"({', '.join(f'{k}: {len(v)}' for k, v in _CACHES.items())})")
    _clear_cache()
    return ret
