import sys
import os.path
from datetime import timedelta
from typing import Callable, AnyStr, Optional, Dict, List, Tuple, Iterable, Generator, Iterator, Set
from collections import defaultdict, OrderedDict
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
def preproc_1(data: List[str]) -> List[str]:
    init_line = "".join(x.strip() for x in data if len(x.strip()) > 0)
    return [x.strip() for x in init_line.split(",")]


def HASH(d: str) -> int:
    r = 0
    for c in d:
        r = ((r + ord(c)) * 17) % 256
    return r


@Task(year=YEAR, day=DAY, task=1)
def task_01(data: List[str], log: Callable[[AnyStr], None]):
    log(f"Init sequence has a length of {len(data)}")
    hashes = [HASH(d=d) for d in data]
    ret = sum(hashes)
    log(f"Sum of HASH values of init sequences is {ret}")
    return ret


@Task(year=YEAR, day=DAY, task=2)
def task_02(data: List[str], log: Callable[[AnyStr], None]):
    box_map = defaultdict(lambda: OrderedDict())

    for instruction in data:
        lbl = instruction.split("-")[0].split("=")[0]
        instruction_hash = HASH(d=lbl)
        if not (0 <= instruction_hash <= 255):
            raise Exception(f"Instruction {instruction} has a HASH of {instruction_hash} outside range")
        if "-" in instruction:
            lbl = instruction.split("-")[0]
            if lbl in box_map[instruction_hash]:
                del box_map[instruction_hash][lbl]
        elif "=" in instruction:
            lbl, focal = instruction.split("=")
            focal = int(focal)
            box_map[instruction_hash][lbl] = focal
        else:
            raise Exception(f"Instruction {instruction} could not be parsed")

    def _calc(_box: int, _slot: int, _focal: int) -> int:
        return (_box + 1) * (_slot + 1) * _focal

    box_powers = {
        idx: sum(_calc(_box=idx, _slot=slot, _focal=focal) for slot, focal in enumerate(box.values()))
        for idx, box in box_map.items()
    }

    return sum(box_powers.values())
