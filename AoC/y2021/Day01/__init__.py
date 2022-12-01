from typing import Callable, AnyStr

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2021, day=1)
def preproc_1(data):
    data = np.array([int(x) for x in data if len(x) > 0], dtype=np.int32)
    return data


_test_in = np.array([199, 200, 208, 210, 200, 207, 240, 269, 260, 263], dtype=np.int32)


@Task(year=2021, day=1, task=1, test_data=[TestData(test_in=_test_in, test_out=7)])
def task01(data, log: Callable[[AnyStr], None]):
    res = _count_inc(data[:-1], data[1:])
    log(f"There are {len(data)} measurements")
    return res


@Task(year=2021, day=1, task=2, test_data=[TestData(test_in=_test_in, test_out=5)])
def task02(data, log: Callable[[AnyStr], None]):
    window_size = 3
    res = 0
    for i in range(window_size + 1, data.shape[0] + 1):
        res += 1 if data[i - window_size - 1:i - 1].sum() < data[i - window_size:i].sum() else 0
    log(f"There are {len(data)} measurements")
    return res


def _count_inc(data1: np.ndarray, data2: np.ndarray):
    return np.sum(data1 < data2)
