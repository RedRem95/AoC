from typing import Callable, AnyStr

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022, day=6)
def preproc_1(data):
    for line in data:
        line = line.strip()
        if len(line) <= 0:
            continue
        return line
    raise Exception()


@Task(year=2022, day=6, task=1)
def task01(data, log: Callable[[AnyStr], None]):
    log(f"Got a datastream of length {len(data)}")
    count = 4
    log(f"Finding \"start of packet\" header in datastream of length {count}")
    res = _detection(line=data, count=count)
    log(f"Found \"start of packet\" header. It ends after {res} symbols")
    return res


@Task(year=2022, day=6, task=2)
def task02(data: str, log: Callable[[AnyStr], None]):
    log(f"Got a datastream of length {len(data)}")
    count = 14
    log(f"Finding Message header in datastream of length {count}")
    res = _detection(line=data, count=count)
    log(f"Found message header. It ends after {res} symbols")
    return res


def _detection(line: str, count: int):
    for i in range(len(line)):
        if len(set(line[i:i + count])) == count:
            return i + count
    return None
