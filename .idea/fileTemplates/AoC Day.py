from typing import Callable, AnyStr, List

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=${WHAT_YEAR}, day=${WHAT_DAY})
def preproc_1(data: List[str]):
    # process data
    return data


@Task(year=${WHAT_YEAR}, day=${WHAT_DAY}, task=1)
def task01(data, log: Callable[[AnyStr], None]):
    # create the result for day 1 task 1
    log("Some very interesting and useful logs")
    return 1


@Task(year=${WHAT_YEAR}, day=${WHAT_DAY}, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    # create the result for day 1 task 2
    return 2