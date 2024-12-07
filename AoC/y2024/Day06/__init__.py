from typing import Callable, AnyStr, Optional, List, Tuple, Dict, Set
import os
import math
from collections import defaultdict
from functools import lru_cache
from time import perf_counter, sleep
from datetime import timedelta

from tqdm import tqdm

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

_DAY = 6

_DIRECTIONS = {
    "^": (-1, 0),
    "v": (1, 0),
    "<": (0, -1),
    ">": (0, 1),
}

_TURN = [_DIRECTIONS["^"], _DIRECTIONS[">"], _DIRECTIONS["v"], _DIRECTIONS["<"]]


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    layout = set()
    pos = None
    for i, l in enumerate(x for x in data if len(x) > 0):
        for j, c in enumerate(l.strip()):
            if c == ".":
                pass
            elif c == "#":
                layout.add((i, j))
            elif c in _DIRECTIONS and pos is None:
                pos = (i, j), _DIRECTIONS[c]
            else:
                raise Exception(f"Do not recognize {c}")
    return pos, (layout, (
        (min(x[0] for x in layout), max(x[0] for x in layout)), (min(x[1] for x in layout), max(x[1] for x in layout))))


@lru_cache(maxsize=None)
def tpl_add(*t):
    return tuple(sum(ts) for ts in zip(*t))


@lru_cache(maxsize=None)
def in_map(pos, bounds):
    p, d = pos
    if all(bounds[i][0] <= p[i] <= bounds[i][1] for i in range(len(p))):
        return True
    return False


def next_move(pos, layout):
    p, d = pos
    pn = tpl_add(p, d)
    if pn in layout:
        d = _TURN[(_TURN.index(d) + 1) % len(_TURN)]
        pn = p
    return pn, d


def simulate_path(start_pos, layout, visited=None):
    layout, bounds = layout
    pos = start_pos
    visited = [] if visited is None else visited.copy()
    while pos not in visited:
        visited.append(pos)
        pos = next_move(pos, layout)
        if not in_map(pos, bounds):
            return visited, 1
    return visited, 2


@Task(year=2024, day=_DAY, task=1, extra_config={"render": True})
def task01(data, log: Callable[[AnyStr], None], render: bool):
    pos, layout = data
    w = layout[1][1][1]
    h = layout[1][0][1]
    log(f"Area has a size of {w}x{h}")
    t1 = perf_counter()
    visited, *_ = simulate_path(pos, layout)
    t2 = perf_counter()
    log(f"Took {timedelta(seconds=t2 - t1)} to simulate path of guard")
    distinct_positions = defaultdict(set)
    for p, d in visited:
        distinct_positions[p].add(d)
    log(f"Guard takes {len(distinct_positions)} steps before leaving the field")
    if render is not None:
        from PIL import Image, ImageDraw
        pixel_size = 10
        offset = math.ceil(pixel_size * 1.5)
        pixel_size3 = pixel_size // 3

        bg = (0, 0, 0)
        rock = (127, 131, 134)
        path = (118, 85, 43)
        start_pos = (127, 127, 239)

        def _lc_to_xy(_l, _c):
            return _c * pixel_size + offset, _l * pixel_size + offset

        def _lc_to_rect(_l, _c):
            _xy = _lc_to_xy(_l=_l, _c=_c)
            return _xy, tpl_add(_xy, (pixel_size, pixel_size))

        img = Image.new("RGB", (offset * 2 + w * pixel_size, offset * 2 + h * pixel_size), bg)
        draw = ImageDraw.Draw(img)
        for l, c in layout[0]:
            draw.rectangle(xy=_lc_to_rect(_l=l, _c=c), fill=rock, outline=rock)
        draw.rectangle(xy=_lc_to_rect(*pos[0]), fill=start_pos, outline=start_pos)
        for p, dirs in distinct_positions.items():
            dirs = set(tuple(abs(y) for y in x) for x in dirs)
            x, y = _lc_to_xy(*p)
            if (1, 0) in dirs:
                draw.rectangle(
                    xy=((x + pixel_size3, y), (x + (pixel_size - pixel_size3), y + pixel_size)),
                    fill=path, outline=path
                )
            if (0, 1) in dirs:
                draw.rectangle(
                    xy=((x, y + pixel_size3), (x + pixel_size, y + (pixel_size - pixel_size3))),
                    fill=path, outline=path
                )
        save_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "p1.png"))
        img.save(save_path)
        log(f"Saved image to {save_path}")

    return len(distinct_positions)


@Task(year=2024, day=_DAY, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    pos, layout = data
    log(f"Area has a size of {layout[1][1][1]}x{layout[1][0][1]}")
    t1 = perf_counter()
    visited, *_ = simulate_path(pos, layout)
    t2 = perf_counter()
    log(f"Simulation of initial path took {timedelta(seconds=t2 - t1)}")
    sleep(.001)
    viable_positions = []
    placed_obstacles = set()
    t1 = perf_counter()
    for i, (start_pos, (obstacle_pos, *_)) in tqdm(enumerate(zip(visited[:], visited[1:])), total=len(visited) - 2,
                                                   desc="Testing positions", leave=False, unit="pos"):
        if start_pos[0] == obstacle_pos or obstacle_pos in placed_obstacles:
            continue
        placed_obstacles.add(obstacle_pos)
        _, break_id = simulate_path(start_pos, (layout[0].union([obstacle_pos]), layout[1]), visited=visited[:i])
        if break_id == 2:
            viable_positions.append(obstacle_pos)
    t2 = perf_counter()
    log(f"Testing every possible position for the new obstacle took {timedelta(seconds=t2 - t1)}")
    log(f"Found {len(placed_obstacles)} possible places for the obstacle so the guard is stuck in a loop")
    return len(viable_positions)
