from typing import Callable, AnyStr, Tuple, List, Set, Optional

import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022, day=14)
def preproc_1(data):
    ret = []
    for i in range(0, len(data), 1):
        line = str(data[i])
        line = line.strip()
        if len(line) <= 0:
            continue
        points = [x.strip().split(",", 1) for x in line.split("->")]
        ret.append([(int(x[0]), int(x[1])) for x in points])
    return ret


@Task(year=2022, day=14, task=1, extra_config={"sand_start": (500, 0)})
def task01(data: List[List[Tuple[int, int]]], log: Callable[[AnyStr], None], sand_start: Tuple[int, int]):
    rocks = _collect_rocks(all_lines=data)
    log(f"There are {len(rocks)} rocks, Sand flows from {sand_start} and cave has no bottom")
    sand = _sim_sand(rocks=rocks, sand_start=sand_start, bottom=False)
    log(f"In the end there are {len(sand)} sand elements")
    return len(sand)


@Task(year=2022, day=14, task=2, extra_config={"sand_start": (500, 0)})
def task02(data: List[List[Tuple[int, int]]], log: Callable[[AnyStr], None], sand_start: Tuple[int, int]):
    rocks = _collect_rocks(all_lines=data)
    log(f"There are {len(rocks)} rocks, "
        f"Sand flows from {sand_start} and cave has a bottom at {max(x[1] for x in rocks) + 2}")
    sand = _sim_sand(rocks=rocks, sand_start=(500, 0), bottom=True)
    log(f"In the end there are {len(sand)} sand elements")
    return len(sand)


def _collect_rocks(all_lines: List[List[Tuple[int, int]]]) -> Set[Tuple[int, int]]:
    rocks: Set[Tuple[int, int]] = set()
    for rock_line in all_lines:
        for i in range(0, len(rock_line) - 1, 1):
            rocks.update(_create_rocks(f=rock_line[i], t=rock_line[i + 1]))
    return rocks


def _create_rocks(f: Tuple[int, int], t: Tuple[int, int]) -> List[Tuple[int, int]]:
    ret = []
    if f[1] == t[1]:
        for i in range(f[0], t[0], np.sign(t[0] - f[0])):
            ret.append((i, f[1]))
    elif f[0] == t[0]:
        for i in range(f[1], t[1], np.sign(t[1] - f[1])):
            ret.append((f[0], i))
    else:
        Exception()
    ret.append(t)
    return ret


def _sim_sand(rocks: Set[Tuple[int, int]], sand_start: Tuple[int, int], bottom: bool) -> Set[Tuple[int, int]]:
    sand = set()

    abyss_start = max(x[1] for x in rocks)
    floor = abyss_start + 2 if bottom else -1

    while True:
        sand_current = sand_start
        while True:
            next_point = _next_sand(current=sand_current, blocked=set().union(rocks, sand), floor=floor)
            if next_point is None:
                sand.add(sand_current)
                if sand_current == sand_start:
                    return sand
                break
            if next_point[1] >= abyss_start and not bottom:
                return sand
            sand_current = next_point


def _next_sand(current: Tuple[int, int], blocked: Set[Tuple[int, int]], floor: int) -> Optional[Tuple[int, int]]:
    next_sand = [(current[0], current[1] + 1), (current[0] - 1, current[1] + 1), (current[0] + 1, current[1] + 1)]
    for n in next_sand:
        if n not in blocked and n[1] != floor:
            return n
    return None
