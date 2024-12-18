from typing import Callable, AnyStr, List, Any, Optional, Dict, Tuple, Iterable, Set, Union
import os
import json
import enum
from queue import LifoQueue

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

_pt_type = np.ndarray


@Preprocessor(year=2021, day=17)
def pre_process_input(data: Any) -> Tuple[_pt_type, _pt_type]:
    line = [x for x in data if len(x) > 0][0].split(":")[-1]
    x_data, y_data = line.split(", ")
    x_min, x_max = x_data.split("=")[-1].split("..")
    y_min, y_max = y_data.split("=")[-1].split("..")

    return np.array((int(x_min), int(x_max))), np.array((int(y_min), int(y_max)))


@Task(year=2021, day=17, task=1)
def run_t1(data: Tuple[_pt_type, _pt_type], log: Callable[[str], None]) -> Any:
    log(
        f"Yeeting the probe into the area span at "
        f"({np.amin(data[0])}, {np.amin(data[1])}) "
        f"w: {np.abs(data[0][0] - data[0][1])}, h: {np.abs(data[1][0] - data[1][1])}"
    )
    paths = simulate_probe(initial=np.array((0, 0)), target_area=data, first=True)
    max_y = -np.inf
    for path in paths:
        max_y = max([max_y] + [pos[1] for pos in path])
    log(f"When you yeet with initial speed of {paths[0][2] - paths[0][0]} you can get a max height of {max_y}")
    return max_y


@Task(year=2021, day=17, task=2)
def run_t2(data: Tuple[_pt_type, _pt_type], log: Callable[[str], None]) -> Any:
    log(
        f"Yeeting the probe into the area span at "
        f"({np.amin(data[0])}, {np.amin(data[1])}) "
        f"w: {np.abs(data[0][0] - data[0][1])}, h: {np.abs(data[1][0] - data[1][1])}"
    )
    paths = simulate_probe(initial=np.array((0, 0)), target_area=data, first=False)
    ret = len(paths)
    log(f"There are {ret} possible ways to yeet the probe in the spot")
    return ret


def simulate_probe(initial: _pt_type, target_area: Tuple[_pt_type, _pt_type], first: bool) -> List[List[_pt_type]]:
    ret: List[List[_pt_type]] = []
    offset: _pt_type = initial.copy()
    initial -= offset
    target_x, target_y = target_area
    target_x -= offset[0]
    target_y -= offset[1]
    target_x = np.sort(target_x)
    target_y = np.sort(target_y)

    x_direction = np.sign(target_x)
    mirror = np.ones_like(offset)
    if (x_direction < 0).all():
        mirror[0] = -1
    target_x *= mirror[0]

    min_x = 0
    max_x = target_x[1]

    min_y = target_y[0]
    max_y = max(200, min_y)

    possible_x = np.arange(start=min_x, stop=max_x + 1, step=1, dtype=int)
    possible_y = np.arange(start=min_y, stop=max_y + 1, step=1, dtype=int)
    change = np.ones_like(offset) * -1

    for j in reversed(range(possible_y.shape[0])):
        for i in range(possible_x.shape[0]):
            current_speed = np.array((possible_x[i], possible_y[j]))
            current_position: _pt_type = initial.copy()

            current_path = [current_position.copy()]

            while can_still_hit(position=current_position, target_area=(target_x, target_y),
                                speed=current_speed):
                current_position += current_speed
                current_path.append(current_position.copy())
                current_speed += change
                if current_speed[0] < 0:
                    current_speed[0] = 0
                if in_target(position=current_position, target_area=(target_x, target_y)):
                    ret.append(current_path)
                    break
            if first and len(ret) > 0:
                break
        if first and len(ret) > 0:
            break

    return [[y * mirror + offset for y in x] for x in ret]


def in_target(position: _pt_type, target_area: Tuple[_pt_type, _pt_type]) -> bool:
    return all(target_area[i][0] <= position[i] <= target_area[i][1] for i in range(position.shape[0]))


def can_still_hit(position: _pt_type, target_area: Tuple[_pt_type, _pt_type], speed: _pt_type) -> bool:
    target_x, target_y = target_area
    if position[0] > target_x[1]:
        return False
    if speed[0] == 0 and position[0] < target_x[0]:
        return False
    if speed[1] < 0 and position[1] < target_y[0]:
        return False

    return True
