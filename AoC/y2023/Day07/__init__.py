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

from .CamelCards import Hand, Card


@Preprocessor(year=2023, day=7)
def preproc_1(data: List[str]) -> List[Tuple[Hand, int]]:
    ret = []
    for line in (x.strip() for x in data if len(x.strip()) > 0):
        cards, bid = [x for x in line.split(" ") if len(x) > 0]
        ret.append((cards, int(bid)))
    return ret


@Preprocessor(year=2023, day=7, task=1)
def preproc_2(data: List[Tuple[str, int]]):
    return [(Hand(cards=[Card(c, False) for c in h]), i) for h, i in data]


@Preprocessor(year=2023, day=7, task=2)
def preproc_3(data: List[Tuple[str, int]]):
    return [(Hand(cards=[Card(c, True) for c in h]), i) for h, i in data]


@Task(year=2023, day=7, task=1)
def task01(data: List[Tuple[Hand, int]], log: Callable[[AnyStr], None]):
    return task(data=data, log=log)


@Task(year=2023, day=7, task=2)
def task02(data: List[Tuple[Hand, int]], log: Callable[[AnyStr], None]):
    return task(data=data, log=log)


def task(data: List[Tuple[Hand, int]], log: Callable[[AnyStr], None]):
    log(f"You play {len(data)} hands")
    log(f"You play {'with' if any(x[0].has_joker_rule() for x in data) else 'without'} joker")
    if any(x[0].has_joker_rule() for x in data):
        log(f"There are {sum(x[0].joker_count() for x in data)} joker in your hands")
    log(f"Max bid is: {max(x[1] for x in data)}")
    sorted_hands = sorted(data, key=lambda x: x[0])
    return sum((i + 1) * b for i, (_, b) in enumerate(sorted_hands))
