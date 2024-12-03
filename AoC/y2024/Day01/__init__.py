from typing import Callable, AnyStr, Optional

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2024, day=1)
def preproc_1(data):
    lists = [], []
    for line in (x for x in data if len(x) > 0):
        i1, i2 = [int(x) for x in line.split(" ") if len(x) > 0]
        lists[0].append(i1)
        lists[1].append(i2)
    return lists


@Task(year=2024, day=1, task=1)
def task01(data, log: Callable[[AnyStr], None]):
    if not all(len(x) == len(data[0]) for x in data):
        raise Exception("Lists are not equal in length")
    log(f"There {len(data)} lists with a length of {len(data[0])}")
    if len(data) != 2:
        raise Exception("There are not 2 lists present. Bad")
    return sum(abs(x-y) for x, y in zip(sorted(data[0]), sorted(data[1])))


@Task(year=2024, day=1, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    from collections import Counter
    if not all(len(x) == len(data[0]) for x in data):
        raise Exception("Lists are not equal in length")
    log(f"There {len(data)} lists with a length of {len(data[0])}")
    if len(data) != 2:
        raise Exception("There are not 2 lists present. Bad")
    c = Counter(data[1])
    return sum(x * c[x] for x in data[0])
