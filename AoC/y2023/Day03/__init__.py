from typing import Callable, AnyStr, Optional, Dict, List, Tuple
from collections import defaultdict
from time import perf_counter
from itertools import chain

import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


def _is_int(v: Optional[str]) -> bool:
    return False if v is None else v.isdigit()


def _surrounds(i: int, j: int) -> List[Tuple[int, int]]:
    return [
        (i, j - 1), (i, j), (i, j + 1),
        (i + 1, j - 1), (i + 1, j), (i + 1, j + 1),
        (i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
    ]


@Preprocessor(year=2023, day=3)
def preproc_1(data):
    ret = []
    for line in (x.strip() for x in data if len(x.strip()) > 0):
        ret.append([])
        for c in line:
            ret[-1].append(None if c == "." else c)
    return ret


def analyse_data(data: List[List[str]]) -> Tuple[List[Tuple[int, List[Tuple[int, int]]]], Dict[str, List[Tuple[int, int]]]]:
    nums = []
    symbols = defaultdict(lambda: [])
    for i, line in enumerate(data):
        cur_num = ""
        cur_idxs = []
        for j, column in enumerate(line):
            if _is_int(column):
                cur_num += column
                cur_idxs.append((i, j))
            else:
                if len(cur_num) > 0:
                    nums.append((int(cur_num), cur_idxs))
                cur_num = ""
                cur_idxs = []
                if column is None:
                    pass
                else:
                    symbols[column].append((i, j))
        if len(cur_num) > 0:
            nums.append((int(cur_num), cur_idxs))
    return nums, symbols


@Task(year=2023, day=3, task=1)
def task01(data: List[List[str]], log: Callable[[AnyStr], None]):
    log(f"Testing grid of size {len(data)}x{max(len(x) for x in data)}")
    t1 = perf_counter()
    nums, symbols = analyse_data(data=data)
    t2 = perf_counter()
    log(f"Analysis of input took {t2-t1:.2}s")
    symbol_pos = set().union(*[_surrounds(*x) for x in chain(*symbols.values())])
    valid_nums = []
    for num, locs in nums:
        if any(loc in symbol_pos for loc in locs):
            valid_nums.append(num)
            pass

    log(f"Found {len(valid_nums)} valid part numbers")
    s = sum(valid_nums)
    log(f"Sum of valid part numbers: {s}")
    return sum(valid_nums)


@Task(year=2023, day=3, task=2, extra_config={"gear_symbol": "*"})
def task02(data: List[List[str]], log: Callable[[AnyStr], None], gear_symbol: str):
    log(f"Testing grid of size {len(data)}x{max(len(x) for x in data)}")
    t1 = perf_counter()
    nums, symbols = analyse_data(data=data)
    t2 = perf_counter()
    log(f"Analysis of input took {t2 - t1:.2}s")

    gear_ratios = []

    log(f"Searching for gears with symbol \"{gear_symbol}\"")

    gears = symbols[gear_symbol]
    for pos in gears:
        surrounds = _surrounds(*pos)
        part_ids = []
        for num, num_locs in nums:
            if any(x in num_locs for x in surrounds):
                part_ids.append(num)
        if len(part_ids) == 2:
            gear_ratios.append(part_ids[0] * part_ids[1])

    log(f"Found {len(gear_ratios)} valid gears")
    s = sum(gear_ratios)
    log(f"Sum of gear ratios: {s}")

    return s
