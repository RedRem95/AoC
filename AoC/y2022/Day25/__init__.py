from typing import Callable, AnyStr

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

from .snafu import from_snafu, to_snafu


@Preprocessor(year=2022, day=25)
def preproc_1(data):
    return [x.strip() for x in data if len(x.strip()) > 0]


@Task(year=2022, day=25, task=1)
def task01(data, log: Callable[[AnyStr], None]):
    _ = from_snafu(value="2=-01")
    for line in data:
        s = line
        v = from_snafu(value=s)
        s2 = to_snafu(value=v)
        log(f"{s:6s} = {v:6d} = {s2}")
    return 0


@Task(year=2022, day=25, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    # create the result for day 1 task 2
    return 1
