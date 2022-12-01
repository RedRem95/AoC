from typing import Callable, AnyStr, List, Any

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022, day=1)
def preprocess(data: List[str]):
    elves = [[]]
    for line in data:
        line = line.strip()
        if len(line) <= 0:
            elves.append([])
        else:
            elves[-1].append(float(line))
    return [x for x in elves if len(x) > 0]


@Task(year=2022, day=1, task=1)
def run_1(data: List[List[float]], log: Callable[[str], None]):
    return int(_calc_top_n(data=data, log=log, n=1))


@Task(year=2022, day=1, task=2)
def run_2(data: List[List[float]], log: Callable[[str], None]):
    return int(_calc_top_n(data=data, log=log, n=3))


def _calc_top_n(data: List[List[float]], n: int, log: Callable[[str], None]) -> float:
    if n <= 0:
        raise Exception()
    log(f"There are {len(data)} elves and {sum(len(x) for x in data)} items")
    food_carried = [sum(x) for x in data]
    food_carried_n = sorted(food_carried, reverse=True)[:n]
    ret = sum(food_carried_n)
    log(f"The top {'elf carries' if n == 1 else f'{n} elves carry'} {ret} calories"
        f"{'' if n == 1 else f' ({food_carried_n})'}")
    return ret
