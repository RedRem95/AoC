from typing import Callable, AnyStr

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor

from .snafu import from_snafu, to_snafu


@Preprocessor(year=2022, day=25)
def preproc_1(data):
    return [x.strip() for x in data if len(x.strip()) > 0]


@Task(year=2022, day=25, task=1)
def task01(data, log: Callable[[AnyStr], None]):
    log(f"Adding {len(data)} values")
    ret = 0
    for line in data:
        value = from_snafu(value=line)
        ret += value
    ret_snafu = to_snafu(value=ret)
    log(f"The sum of {len(data)} values is {ret} or {ret_snafu} in snafu")
    return ret_snafu


@Task(year=2022, day=25, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    # create the result for day 1 task 2
    return 1
