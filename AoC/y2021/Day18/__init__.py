from typing import Callable, AnyStr, List, Any, Optional, Dict, Tuple, Iterable, Set, Union
import os
import json
import enum
from queue import LifoQueue
from itertools import permutations

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

from .snail_math import SnailFishNumber


@Preprocessor(year=2021, day=18)
def pre_process_input(data: Any) -> Any:
    data = [x for x in data if len(x) > 0]
    return data


@Task(year=2021, day=18, task=1)
def run_t1(data: List[str], log: Callable[[str], None]) -> Any:
    log(f"Adding {len(data)} snailfish numbers resulted in:")
    num = SnailFishNumber.parse(data=data[0])
    for line in data[1:]:
        num = SnailFishNumber.add(num, SnailFishNumber.parse(data=line))
    log(str(num))
    mag = num.get_magnitude()
    log(f"with a magnitude of {mag}")
    return mag


@Task(year=2021, day=18, task=2)
def run_t2(data: List[str], log: Callable[[str], Any]) -> Any:
    snail_fish_numbers = [SnailFishNumber.parse(data=x) for x in data]
    combs = list(permutations(range(len(snail_fish_numbers)), 2))
    log(f"Testing {len(combs)} combinations of {len(snail_fish_numbers)} snailfish numbers")
    ret = 0
    best: List[SnailFishNumber] = []
    for i, j in combs:
        if i == j:
            continue
        n1 = snail_fish_numbers[i].copy()
        n2 = snail_fish_numbers[j].copy()
        a = SnailFishNumber.add(n1, n2)
        mag = a.get_magnitude()
        if mag > ret:
            best = [n1, n2, a]
            ret = mag

    log("By adding")
    log(f"{best[0]} +")
    log(f"{best[1]} =")
    log(f"{best[2]}")
    log(f"You get a maximum magnitude of {ret}")

    return ret
