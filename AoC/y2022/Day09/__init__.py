from typing import Callable, AnyStr, List, Tuple

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022, day=9)
def preproc_1(data):
    ret = []
    for line in data:
        line = line.strip()
        if len(line) <= 0:
            continue
        direction, count = line.split(" ")
        ret.append((direction, int(count)))
    return ret


@Task(year=2022, day=9, task=1)
def task01(data: List[Tuple[str, int]], log: Callable[[AnyStr], None]):
    simmed = _sim(sim_data=data, log=log, knot_count=1)
    return len(set(simmed[-1]))


@Task(year=2022, day=9, task=2, extra_config={"knot_count": 9})
def task02(data, log: Callable[[AnyStr], None], knot_count: int):
    simmed = _sim(sim_data=data, log=log, knot_count=knot_count)
    return len(set(simmed[-1]))


def _sim(sim_data: List[Tuple[str, int]], log: Callable[[str], None], knot_count: int) -> List[List[Tuple[int, int]]]:
    if knot_count < 0:
        raise ValueError(f"You cant simulate a rope with less than 0 knots")
    log(f"Simulating a rope with {knot_count} knot{'s' if knot_count != 1 else ''} for {len(sim_data)} steps")
    direction_data = {
        "L": (-1, 0),
        "R": (1, 0),
        "U": (0, 1),
        "D": (0, -1),
    }

    traversed: List[List[Tuple[int, int]]] = [[] for _ in range(knot_count + 1)]
    head, tail = (0, 0), [(0, 0) for _ in range(knot_count)]

    for direction, count in sim_data:
        for _ in range(count):
            head = _add(head, direction_data[direction])
            traversed[0].append(head)
            cur_tail = head
            for i in range(knot_count):
                tail[i] = _move_tail(head=cur_tail, tail=tail[i])
                cur_tail = tail[i]
                traversed[i+1].append(cur_tail)

    log(f"After {len(sim_data)} steps the")
    for i, sub_traversed in enumerate(traversed):
        log(f"{'head' if i == 0 else f'{i}. knot' if i < len(traversed) - 1 else 'tail':>10s} traversed "
            f"{len(sub_traversed)} steps ({len(set(sub_traversed))} unique)")

    return traversed


def _add(t1: Tuple[int, int], t2: Tuple[int, int]) -> Tuple[int, int]:
    return t1[0] + t2[0], t1[1] + t2[1]


def _diff(t1: Tuple[int, int], t2: Tuple[int, int]) -> Tuple[int, int]:
    return t1[0] - t2[0], t1[1] - t2[1]


def _abs(t1: Tuple[int, int]) -> Tuple[int, int]:
    return abs(t1[0]), abs(t1[1])


def _move_tail(head: Tuple[int, int], tail: Tuple[int, int]) -> Tuple[int, int]:
    diff = _diff(t1=head, t2=tail)
    abs_diff = _abs(diff)
    if max(abs_diff) <= 1:
        return tail
    return _add(t1=tail, t2=(int(np.sign(diff[0])), int(np.sign(diff[1]))))
