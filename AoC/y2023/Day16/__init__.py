import sys
import os.path
from datetime import timedelta
from typing import Callable, AnyStr, Optional, Dict, List, Tuple, Iterable, Generator, Iterator, Set
from collections import defaultdict
from time import perf_counter, sleep
from itertools import chain
from functools import lru_cache
from copy import deepcopy
from math import lcm, ceil
import re

from shapely import Polygon, Point
from tqdm import tqdm, trange
import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

# noinspection DuplicatedCode
DAY = int(os.path.basename(os.path.dirname(__file__))[3:])
YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[1:])

RENDER = True

DEFAULT_SPECIAL_OBJECTS: Dict[str, Dict[Tuple[int, int], List[Tuple[int, int]]]] = {
    "/": {(1, 0): [(0, -1)], (-1, 0): [(0, 1)], (0, 1): [(-1, 0)], (0, -1): [(1, 0)]},
    "\\": {(1, 0): [(0, 1)], (-1, 0): [(0, -1)], (0, 1): [(1, 0)], (0, -1): [(-1, 0)]},
    "-": {(1, 0): [(1, 0)], (-1, 0): [(-1, 0)], (0, 1): [(1, 0), (-1, 0)], (0, -1): [(1, 0), (-1, 0)]},
    "|": {(1, 0): [(0, 1), (0, -1)], (-1, 0): [(0, 1), (0, -1)], (0, 1): [(0, 1)], (0, -1): [(0, -1)]},
}

DTS: Dict[Tuple[int, int], str] = {(1, 0): "right", (-1, 0): "left", (0, 1): "down", (0, -1): "up"}


@Preprocessor(year=YEAR, day=DAY)
def preproc_1(data: List[str]) -> Tuple[Dict[Tuple[int, int], str], Tuple[int, int]]:
    data = [x.strip() for x in data if len(x.strip()) > 0]
    ret = {}
    w, h = max(len(x) for x in data), len(data)
    if not all(len(x) == w for x in data):
        raise Exception()
    for i, line in enumerate(data):
        for j, c in enumerate(line):
            if c != ".":
                ret[(j, i)] = c
    return ret, (w, h)


@Task(year=YEAR, day=DAY, task=1, extra_config={"render": RENDER})
def task_01(data: Tuple[Dict[Tuple[int, int], str], Tuple[int, int]], log: Callable[[AnyStr], None], render: bool):
    object_map, (w, h) = data
    return task(
        object_map=object_map, w=w, h=h, log=log, special_objects=DEFAULT_SPECIAL_OBJECTS,
        render_name=os.path.join(os.path.dirname(__file__), "p1.mp4") if render else None
    )


@Task(year=YEAR, day=DAY, task=2, extra_config={"render": RENDER})
def task_02(data: Tuple[Dict[Tuple[int, int], str], Tuple[int, int]], log: Callable[[AnyStr], None], render: bool):
    object_map, (w, h) = data
    starts = []
    for i in range(w):
        starts.append(((i, 0), (0, 1)))
        starts.append(((i, h - 1), (0, -1)))
    for i in range(h):
        starts.append(((0, i), (1, 0)))
        starts.append(((w - 1, i), (-1, 0)))
    return task(
        object_map=object_map, w=w, h=h, log=log, special_objects=DEFAULT_SPECIAL_OBJECTS, starts=starts,
        render_name=os.path.join(os.path.dirname(__file__), "p2.mp4") if render else None
    )


def task(
        object_map: Dict[Tuple[int, int], str], w: int, h: int, log: Callable[[AnyStr], None],
        special_objects: Dict[str, Dict[Tuple[int, int], List[Tuple[int, int]]]],
        starts: List[Tuple[Tuple[int, int], Tuple[int, int]]] = None,
        render_name: Optional[str] = None
):
    if starts is None:
        starts = [((0, 0), (1, 0))]
    log(f"Checking cave of size {w}x{h} with {len(object_map)} objects scattered around it")
    log(f"Starting from {len(starts)} start points")
    t1 = perf_counter()
    energized_fields: Dict[Tuple[Tuple[int, int], Tuple[int, int]], Tuple[List[List[Tuple[int, int]]], int]] = {}
    for start in starts:
        visited, num_energy = simulate(start=start, object_map=object_map, special_objects=special_objects, w=w, h=h)
        visited_points = [[y[0] for y in x] for x in visited]
        energized_fields[start] = (visited_points, num_energy)
    energized_fields_sort = sorted(energized_fields.items(), key=lambda x: x[1][1], reverse=True)
    (max_pos, max_dir), (energized_points, energized_value) = energized_fields_sort[0]
    t2 = perf_counter()
    log(f"You get the maximum energized fields of {energized_value} when starting from {max_pos} going {DTS[max_dir]}")
    log(f"It took {timedelta(seconds=t2-t1)} to check all {len(starts)} starting points ({(t2-t1)/len(starts)}s/point)")
    if render_name is not None:
        f_name = _render(positions=energized_points, object_map=object_map, w=w, h=h, f_name=render_name)
        log(f"Saved rendered video to {f_name}")
    return energized_value


def tpl_add(t1: Tuple[int, ...], t2: Tuple[int, ...]) -> Tuple[int, ...]:
    return tuple(i + j for i, j in zip(t1, t2))


# TODO: optimize using global cache of position and direction
def simulate(
        start: Tuple[Tuple[int, int], Tuple[int, int]],
        object_map: Dict[Tuple[int, int], str], w: int, h: int,
        special_objects: Dict[str, Dict[Tuple[int, int], List[Tuple[int, int]]]]
) -> Tuple[List[List[Tuple[Tuple[int, int], Tuple[int, int]]]], int]:
    frames: List[List[Tuple[Tuple[int, int], Tuple[int, int]]]] = [[start]]
    visited: Set[Tuple[Tuple[int, int], Tuple[int, int]]] = set()
    current: List[Tuple[Tuple[int, int], Tuple[int, int]]] = [start]
    while len(current) > 0:
        new_current = []
        for position, direction in current:
            if not (0 <= position[0] < w and 0 <= position[1] < h):
                continue
            if (position, direction) in visited:
                continue
            visited.add((position, direction))
            if position in object_map:
                for new_direction in special_objects[object_map[position]][direction]:
                    n = (tpl_add(t1=position, t2=new_direction), new_direction)
                    new_current.append(n)
            else:
                n = (tpl_add(t1=position, t2=direction), direction)
                new_current.append(n)
        current = new_current
        frames.append(new_current)
    return frames, len(set(x[0] for x in visited))


def _render(
        positions: List[List[Tuple[int, int]]],
        object_map: Dict[Tuple[int, int], str], w: int, h: int,
        f_name: str
) -> str:
    import imageio as iio

    fps = 60
    block_size = 16
    scale = 1

    bg = (0, 0, 0)
    objects = (127, 131, 134)
    energy = (255, 234, 0)

    visited = set()

    with iio.get_writer(
            f_name, fps=fps, codec="libx264", quality=3, ffmpeg_log_level="quiet", macro_block_size=block_size
    ) as writer:
        sleep(0.01)
        for i in trange(-1, len(positions) + 2 * fps, desc="rendering", leave=False, unit="f"):
            if 0 <= i < len(positions):
                visited.update(positions[i])
            img = _draw_frame(
                w=w, h=h, positions=visited, object_map=object_map, bg=bg, energy=energy, objects=objects
            )
            writer.append_data(_scale_image(img=img, scale=scale, block_size=block_size))

    return f_name


def _draw_frame(
        w: int, h: int, positions: Set[Tuple[int, int]], object_map: Dict[Tuple[int, int], str],
        bg: Tuple[int, int, int], energy: Tuple[int, int, int], objects: Tuple[int, int, int]
) -> np.ndarray:
    from PIL import Image, ImageDraw

    pixel_size = 11

    ret = Image.new("RGB", (w * pixel_size, h * pixel_size), bg)
    draw = ImageDraw.Draw(ret)

    for x in range(w):
        for y in range(h):
            pixel_x, pixel_y = x * pixel_size, y * pixel_size
            if (x, y) in positions:
                draw.rectangle(
                    xy=((pixel_x, pixel_y), (pixel_x + pixel_size, pixel_y + pixel_size)),
                    fill=energy, outline=energy, width=1
                )
            if (x, y) in object_map:
                obj = object_map[(x, y)]
                if obj == "/":
                    draw.line(
                        xy=((pixel_x, pixel_y + pixel_size), (pixel_x + pixel_size, pixel_y)),
                        fill=objects, width=ceil(pixel_size/10)
                    )
                elif obj == "\\":
                    draw.line(
                        xy=((pixel_x, pixel_y), (pixel_x + pixel_size, pixel_y + pixel_size)),
                        fill=objects, width=ceil(pixel_size / 10)
                    )
                elif obj == "-":
                    draw.line(
                        xy=((pixel_x, pixel_y + pixel_size / 2), (pixel_x + pixel_size, pixel_y + pixel_size / 2)),
                        fill=objects, width=ceil(pixel_size / 10)
                    )
                elif obj == "|":
                    draw.line(
                        xy=((pixel_x + pixel_size / 2, pixel_y), (pixel_x + pixel_size / 2, pixel_y + pixel_size)),
                        fill=objects, width=ceil(pixel_size / 10)
                    )
                else:
                    raise Exception(f"Object {obj} could not be rendered")
    return np.array(ret)


# noinspection DuplicatedCode
def _scale_image(img: np.ndarray, scale: int, block_size: int = 1) -> np.ndarray:
    from PIL import Image
    new_size = np.array(list(reversed(img.shape[:2]))) * scale
    new_size = block_size * np.ceil(new_size / block_size).astype(int)
    img = Image.fromarray(img)
    img = img.resize(size=new_size, resample=Image.NEAREST)
    img = np.array(img)
    return img

