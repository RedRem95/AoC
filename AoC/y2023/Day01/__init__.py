from typing import Callable, AnyStr, Optional

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2023, day=1)
def preproc_1(data):
    return [x.strip() for x in data if len(x.strip()) > 0]


nums = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9
}


def _to_int(v: AnyStr, special_allow: bool = False) -> Optional[int]:
    if len(v) < 1:
        return None
    try:
        r = int(v[0])
        return r
    except ValueError:
        pass
    if special_allow:
        for s, n in nums.items():
            if v.startswith(s):
                return n
    return None


def run(data, log: Callable[[AnyStr], None], to_int: Callable[[AnyStr], Optional[int]]):
    log(f"Processing {len(data)} lines of data")
    v = [
        [k for k in (to_int(line[i:]) for i in range(len(line))) if k is not None]
        for line in data
    ]
    if any(len(line) < 2 for line in data):
        raise Exception()
    v = [int(f"{line[0]}{line[-1]}") for line in v]
    log(f"Calibration values: {', '.join(str(x) for x in v)}")
    r = sum(v)
    log(f"Calibration sum:    {r}")
    return r


@Task(year=2023, day=1, task=1)
def task02(data, log: Callable[[AnyStr], None]):
    return run(data=data, log=log, to_int=lambda v: _to_int(v=v, special_allow=False))


@Task(year=2023, day=1, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    return run(data=data, log=log, to_int=lambda v: _to_int(v=v, special_allow=True))
