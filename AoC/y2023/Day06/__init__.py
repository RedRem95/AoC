from typing import Callable, AnyStr, Optional, Dict, List, Tuple, Iterable, Generator, Iterator
from collections import defaultdict
from time import perf_counter
from itertools import chain
from functools import lru_cache
from copy import deepcopy

from tqdm import tqdm
import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2023, day=6)
def preproc_1(data: List[str]) -> List[Tuple[int, int]]:
    race_duration, best_distances = [x.strip() for x in data if len(x.strip()) > 0]
    ret = list(zip((int(x) for x in race_duration.split(":", 1)[1].split(" ") if len(x) > 0), (int(x) for x in best_distances.split(":", 1)[1].split(" ") if len(x) > 0)))
    return ret


def check_race(race_duration: int, best_distance: int) -> Tuple[int, int]:
    min_hold_down = None
    for hold_down in range(1, race_duration):
        distance = hold_down * (race_duration - hold_down)
        if distance > best_distance:
            min_hold_down = hold_down
            break
    return min_hold_down, None if min_hold_down is None else race_duration - min_hold_down


@Task(year=2023, day=6, task=1)
def task01(data: List[Tuple[int, int]], log: Callable[[AnyStr], None]):
    log(f"Simulating {len(data)} races")
    log(f"Max race length: {max(x[0] for x in data)}")
    ways_to_win = []
    for race_duration, best_distance in data:
        min_hold_down, max_hold_down = check_race(race_duration=race_duration, best_distance=best_distance)
        ways_to_win.append(max_hold_down - min_hold_down + 1)
    return np.prod(ways_to_win)


@Task(year=2023, day=6, task=2)
def task02(data: List[str], log: Callable[[AnyStr], None]):
    race_duration = int("".join(str(x[0]) for x in data))
    best_distance = int("".join(str(x[1]) for x in data))
    log(f"Race takes {race_duration}ms and best distance was {best_distance}mm")
    min_hold_down, max_hold_down = check_race(race_duration=race_duration, best_distance=best_distance)
    ret = max_hold_down - min_hold_down + 1
    log(f"Ways to win from {max_hold_down}-{min_hold_down} => {ret} ways to win")
    return ret
