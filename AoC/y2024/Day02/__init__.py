from typing import Callable, AnyStr, Optional, List, Tuple

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

_DAY = 2


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    reports = []
    for line in (x for x in data if len(x) > 0):
        reports.append([int(x) for x in line.split(" ") if len(x) > 0])
    return reports


def _report_safe(report: List[int], valid_range: Tuple[int, int] = (1, 3), acceptable_misses: int = 0) -> bool:
    mi, ma = valid_range
    diffs = [x-y for x, y in zip(report, report[1:])]
    if all(mi <= x <= ma for x in diffs) or all(mi <= -x <= ma for x in diffs):
        return True
    if acceptable_misses <= 0:
        return False
    for i in range(len(report)):
        if _report_safe(report[:i] + report[i+1:], valid_range=valid_range, acceptable_misses=acceptable_misses-1):
            return True
    return False


def run(data, log: Callable[[AnyStr], None], acceptable_misses: int = 0):
    log(f"There are {len(data)} reports present. "
        f"Longest one is {max(len(x) for x in data)}. Shortest is {min(len(x) for x in data)}.")
    log(f"The reactor can sustain {acceptable_misses} bad steps")
    ret = sum(1 if _report_safe(report=x, valid_range=(1, 3), acceptable_misses=acceptable_misses) else 0 for x in data)
    log(f"There are {ret} reports safe. That is {ret/len(data) * 100:.2f}%.")
    return ret


@Task(year=2024, day=_DAY, task=1)
def task01(data, log: Callable[[AnyStr], None]):
    return run(data=data, log=log, acceptable_misses=0)


@Task(year=2024, day=_DAY, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    return run(data=data, log=log, acceptable_misses=1)
