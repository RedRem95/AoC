import sys
import os.path
from datetime import timedelta
from typing import Callable, AnyStr, Optional, Dict, List, Tuple, Iterable, Generator, Iterator, Set
from collections import defaultdict
from time import perf_counter
from itertools import chain
from functools import lru_cache
from copy import deepcopy
from math import lcm, ceil
import re

from shapely import Polygon, Point
from tqdm import tqdm
import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

# noinspection DuplicatedCode
DAY = int(os.path.basename(os.path.dirname(__file__))[3:])
YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[1:])


@Preprocessor(year=YEAR, day=DAY)
def preproc_1(data: List[str]) -> Tuple[np.ndarray, np.ndarray]:
    data = [x.strip() for x in data if len(x.strip()) > 0]
    rows, columns = len(data), max(len(x) for x in data)
    cube_rocks = np.zeros(shape=(rows, columns), dtype=bool)
    round_rocks = np.zeros(shape=(rows, columns), dtype=bool)
    for i, line in enumerate(data):
        for j, char in enumerate(line):
            if char == "O":
                round_rocks[i, j] = True
            elif char == "#":
                cube_rocks[i, j] = True
            elif char == ".":
                pass
            else:
                raise Exception(f"Unknown element {char} in map")
    return cube_rocks, round_rocks


def find_position(data_line: np.ndarray) -> int:
    if len(data_line.shape) != 1:
        raise Exception()
    w = np.where(data_line)[0]
    return w[-1] if len(w) > 0 else -1


def simulate_rocks(cube_rocks: np.ndarray, round_rocks: np.ndarray) -> np.ndarray:
    round_rock_positions: List[Tuple[int, int]] = list(zip(*np.where(round_rocks)))
    round_rocks = round_rocks.copy()
    for row, col in round_rock_positions:
        interesting_data = cube_rocks[:, col][:row] | round_rocks[:, col][:row]
        pos = find_position(data_line=interesting_data)
        round_rocks[row, col] = False
        round_rocks[pos + 1, col] = True
    return round_rocks


def measure_weight(cube_rocks: np.ndarray, round_rocks: np.ndarray, cube_rock_factor: int,
                   round_rock_factor: int) -> int:
    height = cube_rocks.shape[0]

    cube_weight = sum((height - x) * cube_rock_factor for x in np.where(cube_rocks)[0])
    round_weight = sum((height - x) * round_rock_factor for x in np.where(round_rocks)[0])

    return cube_weight + round_weight


@Task(year=YEAR, day=DAY, task=1, extra_config={"render": True})
def task_01(data: Tuple[np.ndarray, np.ndarray], log: Callable[[AnyStr], None], render: bool):
    return task(
        cube_rocks=data[0], round_rocks=data[1], log=log, iterations=1,
        render_name=os.path.join(os.path.dirname(os.path.abspath(__file__)), "p1") if render else None
    )


@Task(year=YEAR, day=DAY, task=2, extra_config={"turn_count": 1000000000, "render": True})
def task_02(data: List[np.ndarray], log: Callable[[AnyStr], None], turn_count: int, render: bool):
    return task(
        cube_rocks=data[0], round_rocks=data[1], log=log, iterations=turn_count * 4,
        render_name=os.path.join(os.path.dirname(os.path.abspath(__file__)), "p2") if render else None
    )


def _do_rotate(cube_rocks: np.ndarray, round_rocks: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    round_rocks = simulate_rocks(cube_rocks=cube_rocks, round_rocks=round_rocks)
    cube_rocks = np.rot90(cube_rocks, axes=(1, 0))
    round_rocks = np.rot90(round_rocks, axes=(1, 0))
    return cube_rocks, round_rocks


def _np_to_tpl(arr: np.ndarray) -> Tuple:
    if len(arr.shape) <= 1:
        return tuple(x for x in arr)
    else:
        return tuple([_np_to_tpl(arr[i]) for i in range(arr.shape[0])])


def task(
        cube_rocks: np.ndarray, round_rocks: np.ndarray, log: Callable[[AnyStr], None], iterations: int,
        render_name: Optional[str] = None
) -> int:
    t1 = perf_counter()
    memory: List[Tuple] = [_np_to_tpl(round_rocks)]
    full_memory: List[np.ndarray] = []
    loop_memory: List[np.ndarray] = []
    post_memory: List[np.ndarray] = []
    full_circles = iterations // 4
    single_iters = iterations - (full_circles * 4)
    loop_count = -1
    log(f"THe field has a size of {cube_rocks.shape[1]}x{cube_rocks.shape[0]}")
    log(f"There are {np.sum(cube_rocks)} cube rocks and {np.sum(round_rocks)} round rocks in the field")
    log(f"Doing {iterations} of turn and tilt. These are {full_circles} full circles, and {single_iters} single iterations")

    for i in range(0, full_circles, 1):
        for j in range(4):
            cube_rocks, round_rocks = _do_rotate(cube_rocks=cube_rocks, round_rocks=round_rocks)
            full_memory.append(np.rot90(round_rocks, k=j + 1, axes=(0, 1)))
        try:
            memory_idx = memory.index(_np_to_tpl(arr=round_rocks))
            loop_memory = full_memory[memory_idx * 4:]
            full_memory = full_memory[:memory_idx * 4]
            loop_part = memory[memory_idx:]
            log(f"Found loop after {i + 1} full circles. Loop has a length of {len(loop_part)}")
            remaining_circles = full_circles - i
            loop_count = remaining_circles / len(loop_part) + 1
            log(f"Loop repeats {loop_count} times")
            round_rocks = np.array(loop_part[remaining_circles % len(loop_part) - 1])
            break
        except ValueError:
            pass
        memory.append(_np_to_tpl(arr=round_rocks))

    for i in range(0, single_iters, 1):
        cube_rocks, round_rocks = _do_rotate(cube_rocks=cube_rocks, round_rocks=round_rocks)
        post_memory.append(np.rot90(round_rocks, k=i + 1, axes=(0, 1)))

    round_rocks = np.rot90(round_rocks, k=single_iters, axes=(0, 1))
    cube_rocks = np.rot90(cube_rocks, k=single_iters, axes=(0, 1))

    ret = measure_weight(cube_rocks=cube_rocks, round_rocks=round_rocks, cube_rock_factor=0, round_rock_factor=1)
    log(f"The round cubes put a weight of {ret} on the northern pillar")
    t2 = perf_counter()

    log(f"Doing {iterations} iterations took {timedelta(seconds=t2-t1)}. {(t2-t1)/iterations}s/iteration")

    if render_name is not None:
        render_name = _render(
            pre_loop=[(cube_rocks, x) for x in full_memory],
            loop=[(cube_rocks, x) for x in loop_memory],
            post_loop=[(cube_rocks, x) for x in post_memory],
            loop_count=loop_count,
            f_name=render_name,
        )
        log(f"Saved rendered representation to {render_name}")
    return ret


def _render(
        pre_loop: List[Tuple[np.ndarray, np.ndarray]],
        loop: List[Tuple[np.ndarray, np.ndarray]], loop_count: int,
        post_loop: List[Tuple[np.ndarray, np.ndarray]],
        f_name: str
) -> str:

    bg_color = (0, 0, 0)
    fg_color = (127, 131, 134)

    frames = ([("Before Loop start", x) for x in pre_loop] +
              [(f"In Loop. Loop repeats {loop_count} times", x) for x in loop] +
              [(f"After the loop", x) for x in post_loop])

    if len(frames) == 1:
        from PIL import Image
        txt, (cube_rocks, round_rocks) = frames[0]
        img = _draw_frame(cube_rocks=cube_rocks, round_rocks=round_rocks, text=txt, bg=bg_color, fg=fg_color)
        f_name = f"{f_name}.png"
        Image.fromarray(img).save(f_name, format="PNG")
        return f_name

    elif len(frames) > 1:
        import imageio as iio

        fps = 3
        block_size = 16
        scale = 1
        f_name = f"{f_name}.mp4"

        with iio.get_writer(
                f_name, fps=fps, codec="libx264", quality=3, ffmpeg_log_level="quiet", macro_block_size=block_size
        ) as writer:
            for txt, (cube_rocks, round_rocks) in tqdm(iterable=frames, desc="rendering", leave=False, unit="f"):
                img = _draw_frame(cube_rocks=cube_rocks, round_rocks=round_rocks, text=txt, bg=bg_color, fg=fg_color)
                writer.append_data(_scale_image(img=img, scale=scale, block_size=block_size))

        return f_name


def _draw_frame(
        cube_rocks: np.ndarray, round_rocks: np.ndarray, text: str, bg, fg
) -> np.ndarray:
    from PIL import Image, ImageDraw, ImageFont
    if text is None:
        text = ""

    pixel_size = 10
    margin = ceil(pixel_size / 2)
    text_height = 0 if len(text) <= 0 else pixel_size * 2 + margin

    img_width = cube_rocks.shape[1] * pixel_size + margin * 2
    img_height = cube_rocks.shape[0] * pixel_size + margin * 2 + text_height

    ret = Image.new("RGB", size=(img_width, img_height), color=bg)
    draw = ImageDraw.Draw(ret)

    for row, col in zip(*np.where(cube_rocks)):
        x, y = col * pixel_size + margin, row * pixel_size + margin
        draw.rectangle(xy=((x, y), (x + pixel_size, y + pixel_size)), fill=fg, outline=fg, width=1)

    for row, col in zip(*np.where(round_rocks)):
        x, y = col * pixel_size + margin, row * pixel_size + margin
        draw.ellipse(xy=((x, y), (x + pixel_size, y + pixel_size)), fill=fg, outline=fg, width=1)

    if text_height > 0:
        font = ImageFont.truetype(font="arial.ttf", size=text_height)
        x, y = margin, img_height - text_height
        draw.text(
            xy=(x, y), text=text, fill=fg, font=font, stroke_width=ceil(pixel_size / 10), stroke_fill=fg, anchor="lt"
        )

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
