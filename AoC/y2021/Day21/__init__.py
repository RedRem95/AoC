from typing import Callable, AnyStr, List, Any, Optional, Dict, Tuple, Iterable, Set, Union, Iterator
import os
import json
import enum
import queue
import itertools
from queue import LifoQueue
from itertools import permutations
from functools import lru_cache

import numpy as np
from scipy.spatial import distance
from scipy.signal import convolve2d
import matplotlib
import matplotlib.pyplot as plt

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


_get_die = Callable[[int], int]


@Preprocessor(year=2021, day=21)
def pre_process_input(data: Any) -> Any:
    data = [x for x in data if len(x) > 0]
    p1 = int(data[0].split(":")[-1])
    p2 = int(data[1].split(":")[-1])
    return p1, p2


@Task(year=2021, day=21, task=1)
def run_t1(data: Tuple[int, int], log: Callable[[str], None]) -> Any:

    _deterministic_die = [0]

    def roll_deterministic_die(times: int) -> int:
        _ret = 0
        for _ in range(times):
            _ret += _deterministic_die[0] + 1
            _deterministic_die[0] = (_deterministic_die[0] + 1) % 100
        return _ret

    points, rounds_played = play_game(
        start_p1=data[0], start_p2=data[1], die=roll_deterministic_die, target_points=1000
    )
    ret = points[rounds_played % len(points)] * rounds_played * 3
    log(f"You played {rounds_played} rounds of 'Dirac Dice' with the fully deterministic die and didnt split reality. WP")
    for i, pts in enumerate(points):
        log(f"  player {i + 1} made {pts} points{' <- Winner' if pts == max(points) else ''}")
    return ret


# @Task(year=2021, day=21, task=2)
def run_t2(data: Tuple[int, int], log: Callable[[str], None]) -> Any:
    wins: Tuple[int, int] = play_q_game(data[0], data[1], 0, 0, True, 0, 0)
    num_realities = sum(wins)
    ret = max(wins)
    log(f"While playing 'Dirac Dice' with the quantum die you split the reality in {num_realities} versions")
    for i, win in enumerate(wins):
        log(f"  player {i + 1} won in {win}{' <- Winner' if win == ret else ''}")
    return ret


def play_game(start_p1: int, start_p2: int, die: _get_die, target_points) -> Tuple[Tuple[int, ...], int]:
    pos: List[int] = [start_p1, start_p2]
    points: List[int] = [0, 0]
    i = 0
    while all(p < target_points for p in points):
        pos[i % 2] = (pos[i % 2] + die(3))
        while pos[i % 2] > 10:
            pos[i % 2] -= 10
        points[i % 2] += pos[i % 2]
        i += 1

    return tuple(points), i


def add_tuple(x: Tuple[int, ...], y: Tuple[int, ...]) -> Tuple[int, ...]:
    return tuple(a + b for a, b in zip(x, y))


@lru_cache()
def play_q_game(
        position_p1: int, position_p2: int, score_p1: int, score_p2: int, turn_p1: bool, cur_roll: int, rolls: int
) -> Tuple[int, int]:
    if score_p1 >= 21:
        return 1, 0
    if score_p2 >= 21:
        return 0, 1
    out = (0, 0)
    if rolls != 3:
        for i in range(1, 4):
            out = add_tuple(
                out,
                play_q_game(position_p1, position_p2, score_p1, score_p2, turn_p1, cur_roll + i, rolls + 1)
            )
    else:
        cur = position_p1 if turn_p1 else position_p2
        cur += cur_roll
        cur = ((cur - 1) % 10) + 1
        if turn_p1:
            out = add_tuple(
                out,
                play_q_game(cur, position_p2, score_p1 + cur, score_p2, not turn_p1, 0, 0)
            )
        else:
            out = add_tuple(
                out,
                play_q_game(position_p1, cur, score_p1, score_p2 + cur, not turn_p1, 0, 0)
            )
    return out
