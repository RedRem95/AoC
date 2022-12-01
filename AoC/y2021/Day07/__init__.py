from typing import Callable, AnyStr, List, Any, Optional, Dict, Tuple, Iterable
import os
import json

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2021, day=7)
def pre_process_input( data: Any) -> Any:
    ret: np.ndarray = np.array([int(x) for x in data[0].split(",")], dtype=int)
    return ret


@Task(year=2021, day=7, task=1)
def run_t1(data: np.ndarray, log) -> Any:
    return _run(data=data, log=log)


@Task(year=2021, day=7, task=2)
def run_t2(data: Any, log) -> Any:
    def f(t):
        return ((t + 1) * t) / 2

    return _run(data=data, f=f, log=log)


def _run(data: np.ndarray, log: Callable[[AnyStr], None], f: Optional[Callable[[int], int]] = None):
    mi, ma = np.min(data), np.max(data)
    best = np.inf
    tar_pos = -1
    no_kernel = f is None
    if f is None:
        def f(x):
            return x
    for i in range(mi + 1, ma, 1):
        this = np.sum(f(np.abs(data - i)), dtype=int)
        if this < best:
            best = this
            tar_pos = i
    log(f"There are {data.shape[0]} craps helping. How nice")
    log(f"Using {'no' if no_kernel else 'a'} kernel to adjust values")
    log(f"Craps will go to target position {tar_pos}")
    return best
