from typing import Callable, AnyStr, Optional, Dict, List, Tuple, Iterable, Generator, Iterator
from collections import defaultdict
from time import perf_counter
from itertools import chain
from functools import lru_cache
from copy import deepcopy

from tqdm import tqdm
import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


def _sort_and_check(lst: List[Tuple[int, int, int]], full_check: bool = False):
    lst = sorted(lst, key=lambda x: x[0])
    if any(lst[i][1] > lst[i + 1][0] for i in range(len(lst) - 1)):
        raise Exception()
    if full_check and any(lst[i][1] + 1 != lst[i + 1][0] for i in range(len(lst) - 1)):
        raise Exception()
    return lst


@Preprocessor(year=2023, day=5)
def preproc_1(data: List[str]) -> Tuple[List[int], Dict[str, Dict[str, List[Tuple[int, int, int]]]]]:
    seeds: List[int] = []
    maps: Dict[str, Dict[str, List[Tuple[int, int, int]]]] = defaultdict(lambda: defaultdict(list))
    cur_map: Optional[Tuple[str, str]] = None
    max_origin = 0
    for line in (x.strip() for x in data):
        if line.startswith("seeds:"):
            seeds = [int(x) for x in (y for y in line.split(":", 1)[-1].split(" ") if len(y.strip()) > 0)]
            max_origin = max(max_origin, *seeds)
        elif "map" in line:
            _ = line.strip().split(" ")[0].split("-")
            cur_map = (_[0], _[2])
        elif len(line.strip()) > 0:
            dst, org, rng = [int(x) for x in line.strip().split(" ") if len(x.strip()) > 0]
            maps[cur_map[0]][cur_map[1]].append((org, org + rng - 1, dst))
            if any(x < 0 for x in maps[cur_map[0]][cur_map[1]][-1]):
                raise Exception()
            max_origin = max(max_origin, org + rng - 1, dst + rng - 1)
    for k1 in maps.keys():
        for k2 in maps[k1].keys():
            maps[k1][k2] = _sort_and_check(lst=maps[k1][k2], full_check=False)
            n_l = []
            ptr = 0
            for o1, o2, d in maps[k1][k2]:
                if o1 > ptr:
                    n_l.append((ptr, o1 - 1, ptr))
                n_l.append((o1, o2, d))
                ptr = o2 + 1
            if ptr < max_origin:
                n_l.append((ptr, max_origin, ptr))
            maps[k1][k2] = _sort_and_check(lst=n_l, full_check=True)
    return seeds, maps


def process_map(
        seeds: List[Tuple[int, int]],
        maps: Dict[str, Dict[str, List[Tuple[int, int, int]]]],
        target: str,
        origin: str = "seed",
        log: Callable[[AnyStr], None] = lambda s: None,
        total: Optional[int] = None
) -> int:
    if total is not None:
        log(f"There are {total} seeds")
    log(f"You are trying to get the ids from {origin} to {target}")
    t1 = perf_counter()
    maps = simplify_map(maps=maps, origin=origin, target=target)
    t2 = perf_counter()
    log(f"Map simplification took {t2 - t1:.4f}s")
    origin_to_target = maps[origin][target]
    merged = merge_range_lists(l1=[(x[0], x[1], x[0]) for x in seeds], l2=origin_to_target)
    return min(x[-1] for x in merged)


def simplify_map(maps: Dict[str, Dict[str, List[Tuple[int, int, int]]]], target: str, origin: str) -> Dict[str, Dict[str, List[Tuple[int, int, int]]]]:
    maps = deepcopy(maps)
    done_steps = {origin}
    while not target in maps[origin]:
        step = [x for x in maps[origin].keys() if x in maps and x not in done_steps][0]
        done_steps.add(step)
        for new_target in list(maps[step].keys()):
            l1 = sorted(maps[origin][step], key=lambda x: x[0])
            l2 = sorted(maps[step][new_target], key=lambda x: x[0])
            l3 = merge_range_lists(l1=l1, l2=l2)
            maps[origin][new_target] = _sort_and_check(lst=l3, full_check=True)
    return maps


def merge_range_lists(l1: List[Tuple[int, int, int]], l2: List[Tuple[int, int, int]]):
    l3 = []
    for o1, o2, d1 in l1:
        d2 = d1 + o2 - o1
        for o21, o22, d21 in l2:
            d22 = d21 + o22 - o21
            if o21 <= d1 <= o22 <= d2:
                rng = o22 - d1
                off = d1 - o21
                l3.append((o1, o1 + rng, d21 + off))
            elif d1 <= o21 <= o22 <= d2:
                rng = o22 - o21
                off = o21 - d1
                l3.append((o1 + off, o1 + off + rng, d21))
            elif d1 <= o21 <= d2 <= o22:
                rng = d2 - o21
                off = o21 - d1
                l3.append((o1 + off, o1 + off + rng, d21))
            elif o21 <= d1 <= d2 <= o22:
                rng = d2 - d1
                off = d1 - o21
                l3.append((o1, o1 + rng, d21 + off))
    return l3


@Task(year=2023, day=5, task=1)
def task01(data: Tuple[List[int], Dict[str, Dict[str, List[Tuple[int, int, int]]]]], log: Callable[[AnyStr], None]):
    seeds, maps = data
    target, origin = "location", "seed"
    min_id = process_map(seeds=[(x, x) for x in seeds], total=len(seeds), maps=maps, target=target, origin=origin, log=log)
    log(f"Minimum {target} id is {min_id}")
    return min_id


@Task(year=2023, day=5, task=2)
def task02(data: Tuple[List[int], Dict[str, Dict[str, List[Tuple[int, int, int]]]]], log: Callable[[AnyStr], None]):
    seeds, maps = data
    pairs = []
    for i in range(0, len(seeds), 2):
        pairs.append((seeds[i], seeds[i] + seeds[i+1]))
    pairs = sorted(pairs)
    total = sum(x[1] - x[0] for x in pairs)
    target, origin = "location", "seed"
    min_id = process_map(pairs, total=total, maps=maps, target=target, origin=origin, log=log)
    log(f"Minimum {target} id is {min_id}")
    return min_id
