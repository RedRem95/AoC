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


_LR = {
    "L": 0,
    "R": 1
}


@Preprocessor(year=2023, day=8)
def preproc_1(data: List[str]) -> Tuple[List[str], Dict[str, Tuple[str, str]]]:
    ret = {}
    data = [x.strip() for x in data if len(x.strip()) > 0]
    for line in data[1:]:
        o, t = line.split("=")
        tl, tr = t.split(",")
        tl = str(tl).strip(" ()").upper()
        tr = str(tr).strip(" ()").upper()
        o = o.strip().upper()
        if o in ret:
            raise Exception()
        ret[o] = (tl, tr)
    return [x for x in data[0]], ret


def navigate(network:  Dict[str, Tuple[str, str]], instructions: List[str], start: str, goals: Set[str]) -> Tuple[int, str]:
    steps = 0
    cur: str = start
    while cur not in goals:
        instruction = instructions[steps % len(instructions)]
        steps += 1
        cur = network[cur][_LR[instruction]]
    return steps, cur


@Task(year=2023, day=8, task=1)
def task01(data: Tuple[List[str], Dict[str, Tuple[str, str]]], log: Callable[[AnyStr], None]):
    start = "AAA"
    goal = "ZZZ"

    instructions, network = data

    all_nodes = set().union(network.keys(), [x[0] for x in network.values()], [x[1] for x in network.values()])
    if any(x not in network.keys() for x in all_nodes):
        raise Exception()

    log(f"Starting at {start} and trying to get to {goal}")
    log(f"The instructions repeat after {len(instructions)} steps")
    log(f"The network has {len(all_nodes)} nodes")

    steps = navigate(network=network, instructions=instructions, start=start, goals={goal})[0]

    log(f"It takes {steps} steps to get through the desert from {start} to {goal}")
    return steps


@Task(year=2023, day=8, task=2)
def task02(data: Tuple[List[str], Dict[str, Tuple[str, str]]], log: Callable[[AnyStr], None]):
    instructions, network = data

    start_end, goal_end = "A", "Z"

    all_nodes = set().union(network.keys(), [x[0] for x in network.values()], [x[1] for x in network.values()])
    if any(x not in network.keys() for x in all_nodes):
        raise Exception()

    starts = {x for x in network.keys() if x.endswith(start_end)}
    goals = {x for x in network.keys() if x.endswith(goal_end)}

    log(f"Starting at any node ending with      {start_end}. These are {len(starts)} nodes")
    log(f"Trying to get to any node ending with {goal_end}. These are {len(goals)} nodes")

    log(f"The instructions repeat after {len(instructions)} steps")
    log(f"The network has {len(all_nodes)} nodes")

    t1 = perf_counter()
    steps = [navigate(network=network, instructions=instructions, start=x, goals=goals) for x in starts]
    t2 = perf_counter()

    log(f"It takes {t2-t1:.6f}s to calculate all {len(steps)} paths through the network")
    log(f"The {len(steps)} paths"
        f"{'' if len(set(x[1] for x in steps)) == len(steps) else ' dont'} end up on different nodes")
    log(f"Min step count: {min(x[0] for x in steps)}; Max step count: {max(x[0] for x in steps)}")

    t1 = perf_counter()
    steps = lcm(*[x[0] for x in steps])
    t2 = perf_counter()

    log(f"The lcm calculation takes {t2-t1:.6f}s for the {len(starts)} path step counts")

    log(f"It takes {steps} steps to get "
        f"from all {len(starts)} nodes ending on {start_end} "
        f"to any of the {len(goals)} nodes ending in {goal_end}")

    return steps

