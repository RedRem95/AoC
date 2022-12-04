from typing import Callable, AnyStr, List, Tuple

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022, day=4)
def preproc_1(data):
    ret = []
    for line in data:
        line = str(line).strip()
        if len(line) <= 0:
            continue
        e1, e2 = line.split(",")
        e11, e12 = e1.split("-")
        e21, e22 = e2.split("-")
        ret.append(((int(e11), int(e12)), (int(e21), int(e22))))
    return ret


@Task(year=2022, day=4, task=1)
def task01(data: List[Tuple[Tuple[int, int], Tuple[int, int]]], log: Callable[[AnyStr], None]):
    log(f"There are {len(data)} pairs of elves. So {len(data) * 2}")
    s = 0
    for e1, e2 in data:
        if (e1[0] <= e2[0] and e1[1] >= e2[1]) or (e2[0] <= e1[0] and e2[1] >= e1[1]):
            s += 1
    log(f"In {s} pairs of elves one might be workless :(")
    return s


@Task(year=2022, day=4, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    log(f"There are {len(data)} pairs of elves. So {len(data) * 2}")
    s = 0
    for e1, e2 in data:
        e1_r = set(range(e1[0], e1[1] + 1))
        e2_r = set(range(e2[0], e2[1] + 1))
        intersection = e1_r.intersection(e2_r)
        if len(intersection) > 0:
            s += 1
    log(f"In {s} pairs there are overlaps. These should be addressed maybe")
    return s
