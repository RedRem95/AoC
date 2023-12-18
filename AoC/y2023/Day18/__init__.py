import sys
import os.path
from datetime import timedelta
from typing import Callable, AnyStr, Optional, Dict, List, Tuple, Iterable, Generator, Iterator, Set, Deque
from collections import defaultdict, OrderedDict
from time import perf_counter
from itertools import chain
from functools import lru_cache
from copy import deepcopy
from math import lcm, ceil
import re
from queue import PriorityQueue, Queue
from operator import xor

from shapely import Polygon, Point, LineString
from tqdm import tqdm
import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

from ..Day17 import tpl_add, tpl_mult, tpl_dist

# noinspection DuplicatedCode
DAY = int(os.path.basename(os.path.dirname(__file__))[3:])
YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[1:])

RENDER = True

DIRECTIONS = {
    "U": (-1, 0),  # U -> L inner; U -> R outer
    "D": (1, 0),  # D -> L outer; D -> R inner
    "L": (0, -1),  # L -> U outer; L -> D inner
    "R": (0, 1),  # R -> U inner; R -> D outer
}

DIRECTION_ENCODING = {
    "0": "R",
    "1": "D",
    "2": "L",
    "3": "U",
}

TURN_MODIFIER = {
    "U": {"L": False, "R": True},
    "D": {"L": True, "R": False},
    "L": {"U": True, "D": False},
    "R": {"U": False, "D": True},
}


@Preprocessor(year=YEAR, day=DAY)
def preproc_1(data: List[str]) -> List[Tuple[str, int, str]]:
    ret = []
    for line in (x.strip() for x in data if len(x.strip()) > 0):
        direction, steps, color = line.split(" ")
        color = color[1:-1]
        steps = int(steps)
        ret.append((direction, steps, color))
    return ret


@Preprocessor(year=YEAR, day=DAY, task=2)
def preproc_2(data: List[Tuple[str, int, str]]) -> List[Tuple[str, int, str]]:
    ret = []
    for direction, steps, color in data:
        new_steps = int(color[1:-1], base=16)
        new_direction = DIRECTION_ENCODING[color[-1]]
        ret.append((new_direction, new_steps, color))
    return ret


@Task(year=YEAR, day=DAY, task=1, extra_config={"render": RENDER})
def task_01(data: List[Tuple[str, int, str]], log: Callable[[AnyStr], None], render: bool):
    return task(
        instructions=data, log=log,
        render_name=os.path.join(os.path.dirname(__file__), "p1.png") if render else None
    )


@Task(year=YEAR, day=DAY, task=2, extra_config={"render": RENDER})
def task_02(data: List[Tuple[str, int, str]], log: Callable[[AnyStr], None], render: bool):
    return task(
        instructions=data, log=log,
        render_name=os.path.join(os.path.dirname(__file__), "p2.png") if render else None
    )


def task(instructions: List[Tuple[str, int, str]], log: Callable[[AnyStr], None], render_name: Optional[str]):
    log(f"Creating trench from {len(instructions)} instructions")
    points = [(0, 0)]
    for i in range(len(instructions)):
        direction, steps, color = instructions[i]
        next_direction = instructions[(i + 1) % len(instructions)][0]
        prev_direction = instructions[i - 1][0]

        direction_tpl = DIRECTIONS[direction]

        i_o_next = TURN_MODIFIER[direction][next_direction]
        i_o_prev = TURN_MODIFIER[prev_direction][direction]

        turn_modifier = 1 if i_o_next and i_o_prev else 0 if i_o_next or i_o_prev else -1

        points.append(tpl_add(t1=points[-1], t2=tpl_mult(t1=direction_tpl, mult=steps + turn_modifier)))
    if points[-1] != points[0]:
        log(f"Loop does not close")
    poly = Polygon(((x, y) for y, x in points))

    min_x, min_y, max_x, max_y = poly.bounds
    w, h = int(max_x - min_x), int(max_y - min_y)

    log(f"The resulting trench has a size of {w}x{h}")

    if render_name is not None:
        from PIL import Image, ImageDraw

        scale = 2000 / max(w, h)
        offset = 30
        img = Image.new("RGB", (ceil(w * scale + 2 * offset), ceil(h * scale + 2 * offset)))
        img_draw = ImageDraw.Draw(img)

        for (y1, x1), (y2, x2), color in zip(points, points[1:], (x[2] for x in instructions)):

            x1, y1 = (x1 - min_x) * scale + offset, (y1 - min_y) * scale + offset
            x2, y2 = (x2 - min_x) * scale + offset, (y2 - min_y) * scale + offset

            img_draw.line(xy=((x1, y1), (x2, y2)), fill=color, width=5)

        img.save(render_name)
        log(f"Saved image to {render_name}")

    return int(poly.area)
