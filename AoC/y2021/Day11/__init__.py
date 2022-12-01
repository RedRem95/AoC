from typing import Callable, AnyStr, List, Any, Optional, Dict, Tuple, Iterable
import os
import json
import enum
from queue import LifoQueue

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2021, day=11)
def pre_process_input(data: Any) -> Any:
    data = [x for x in data if len(x) > 0]
    ret = np.array([[int(x) for x in y] for y in data])
    return ret


@Task(year=2021, day=11, task=1)
def run_t1(data: np.ndarray, log: Callable[[str], None]) -> Any:
    data = data.copy()
    log(f"There are {np.product(data.shape)} octopuses in the area")
    flashes = 0
    n = 100

    for _ in range(n):
        data = _do_step(data=data)
        to_flash = data > 9
        flashes += np.sum(to_flash)
        data[to_flash] = 0

    log(f"After {n} iterations you were able to observe {flashes} flashes")

    return flashes


@Task(year=2021, day=11, task=2)
def run_t2(data: np.ndarray, log: Callable[[str], None]) -> Any:
    data = data.copy()
    log(f"There are {np.product(data.shape)} octopuses in the area")
    flashes = 0
    k = 0
    while True:
        data = _do_step(data=data)
        to_flash = data > 9
        flashes += np.sum(to_flash)
        k += 1
        if to_flash.all():
            break
        data[to_flash] = 0
    log(f"After {k} iterations and {flashes} flashes all are in sync")

    return k


def _do_step(data: np.ndarray) -> np.ndarray:
    data = data + 1
    flashed = np.zeros(shape=data.shape, dtype=bool)
    while True:
        new_flashes = np.logical_and(np.logical_not(flashed), data > 9)
        if not new_flashes.any():
            break
        flashed = np.logical_or(flashed, new_flashes)
        for i in (-1, 0, 1):
            d_view = data[:, :]
            f_view = new_flashes[:, :]
            if i > 0:
                d_view = d_view[i:, :]
                f_view = f_view[:-i, :]
            elif i < 0:
                d_view = d_view[:i, :]
                f_view = f_view[-i:, :]
            for j in (-1, 0, 1):
                d_view_2 = d_view[:, :]
                f_view_2 = f_view[:, :]
                if j > 0:
                    d_view_2 = d_view[:, j:]
                    f_view_2 = f_view[:, :-j]
                elif j < 0:
                    d_view_2 = d_view[:, :j]
                    f_view_2 = f_view[:, -j:]
                d_view_2[f_view_2] += 1

    return data
