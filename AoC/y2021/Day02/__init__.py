from typing import Callable, AnyStr, List, Any

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2021, day=2)
def preproc(data: List[str]) -> Any:
    return [x.split(" ")[:2] for x in data if len(x) > 0]


@Task(year=2021, day=2, task=1)
def run_t1(data, log: Callable[[AnyStr], None]):
    pos = np.array([0, 0, 0])
    move = {
        "forward": np.array([1, 0, 1]),
        "up": np.array([0, -1, 1]),
        "down": np.array([0, 1, 1])
    }
    for t, v in data:
        pos += move[t] * int(v)
    log("\n".join([
        f"Ending position:   ({pos[0]}, {pos[1]})",
        f"Total units moved: {pos[2]}",
        f"Direct distance:   {np.sqrt(np.sum(np.square(pos[:2]))):.2f}"
    ]))
    return np.prod(pos[:2])


@Task(year=2021, day=2, task=2)
def run_t2(data: Any, log) -> Any:
    pos = np.array([0, 0, 0, 0])
    move = {
        "forward": lambda: np.array([1, pos[-1], np.abs(pos[-1]), 0]),
        "up": lambda: np.array([0, 0, 0, -1]),
        "down": lambda: np.array([0, 0, 0, 1])
    }
    for t, v in data:
        pos += move[t]() * int(v)
    log("\n".join([
        f"Ending position:   ({pos[0]}, {pos[1]})",
        f"Ending aim:        {pos[-1]}",
        f"Total units moved: {pos[2]}",
        f"Direct distance:   {np.sqrt(np.sum(np.square(pos[:2]))):.2f}"
    ]))
    return np.prod(pos[:2])
