import os.path
from datetime import timedelta
from typing import Callable, AnyStr, Optional, Dict, List, Tuple, Iterable, Generator, Iterator, Set
from collections import defaultdict
from time import perf_counter
from itertools import chain
from functools import lru_cache
from copy import deepcopy
from math import lcm, ceil

from shapely import Polygon, Point
from tqdm import tqdm
import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

PIPES: Dict[str, List[Tuple[int, int]]] = {
    "|": [(1, 0), (-1, 0)],
    "-": [(0, 1), (0, -1)],
    "L": [(-1, 0), (0, 1)],
    "J": [(-1, 0), (0, -1)],
    "7": [(1, 0), (0, -1)],
    "F": [(1, 0), (0, 1)]
}


@Preprocessor(year=2023, day=10)
def preproc_1(data: List[str]) -> Tuple[Tuple[int, int], Dict[Tuple[int, int], List[Tuple[int, int]]]]:
    start: Tuple[int, int] = (-1, -1)
    ret: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
    for i, line in enumerate(x.strip() for x in data if len(x.strip()) > 0):
        for j, c in enumerate(x.strip() for x in line if len(x.strip()) > 0):
            if c == ".":
                continue
            elif c == "S":
                start = (i, j)
            elif c in PIPES:
                ret[(i, j)] = [(i + di, j + dj) for di, dj in PIPES[c]]
            else:
                raise Exception(f"{c} could not be processed")
    if any(x < 0 for x in start):
        raise Exception()
    ret[start] = []
    for o, t in ret.items():
        if start in t:
            ret[start].append(o)
    if len(ret[start]) != 2:
        raise Exception()
    return start, ret


@Task(year=2023, day=10, task=1)
def task01(data: Tuple[Tuple[int, int], Dict[Tuple[int, int], List[Tuple[int, int]]]], log: Callable[[AnyStr], None]):
    start, network = data
    x_bound = (min(x[1] for x in network.keys()), max(x[1] for x in network.keys()))
    y_bound = (min(x[0] for x in network.keys()), max(x[0] for x in network.keys()))
    log(f"The interesting area has a size of {x_bound[1] - x_bound[0]}x{y_bound[1] - y_bound[0]}")
    visited = {start: 0}
    current = [start]
    while len(current) != 0:
        c = current.pop()
        steps = visited[c]
        next_steps = [x for x in network[c] if x in network]
        for ns in next_steps:
            if ns not in visited or steps + 1 < visited[ns]:
                visited[ns] = steps + 1
                current.append(ns)
    return max(visited.values())


@Task(year=2023, day=10, task=2, extra_config={"create_image": True})
def task02(
        data: Tuple[Tuple[int, int], Dict[Tuple[int, int], List[Tuple[int, int]]]],
        log: Callable[[AnyStr], None],
        create_image: bool = False
):
    start, network = data
    x_bound = (min(x[1] for x in network.keys()), max(x[1] for x in network.keys()))
    y_bound = (min(x[0] for x in network.keys()), max(x[0] for x in network.keys()))
    log(f"The interesting area has a size of {x_bound[1] - x_bound[0]}x{y_bound[1] - y_bound[0]}")
    t1 = perf_counter()
    loop: List[Tuple[int, int]] = [start]
    while loop[-1] != loop[0] or len(loop) <= 1:
        fount = False
        for p_next in network[loop[-1]]:
            if p_next not in loop:
                loop.append(p_next)
                fount = True
                break
        if not fount:
            if loop[0] in network[loop[-1]]:
                loop.append(loop[0])
            else:
                raise Exception()
    loop = loop[:-1]
    poly = Polygon(loop)
    t2 = perf_counter()
    log(f"Loop creation took {timedelta(seconds=t2 - t1)}")
    log(f"Loop has a length of {len(loop)}")
    furthest_point = (len(loop) // 2, loop[len(loop) // 2])
    num_points = (x_bound[1] - x_bound[0] + 1) * (y_bound[1] - y_bound[0] + 1) - len(loop)
    log(f"Need to check {num_points} points for inside and outside")
    t1 = perf_counter()
    in_out = {}
    with tqdm(total=num_points, desc="Checking points for in/out", leave=False, unit="p") as pb:
        for i in range(y_bound[0], y_bound[1] + 1, 1):
            for j in range(x_bound[0], x_bound[1] + 1, 1):
                p = (i, j)
                if p not in loop:
                    in_out[p] = poly.contains(Point(*p))
                    pb.update(n=1)
    t2 = perf_counter()
    log(f"In/Out checking took {timedelta(seconds=t2 - t1)}")
    count_in_loop = sum(in_out.values())
    count_out_loop = sum(1 if x is False else 0 for x in in_out.values())
    log(f"{count_in_loop}/{num_points} ({100 * count_in_loop / num_points:.2f}%) are contained in the pipe loop")
    log(f"{count_out_loop}/{num_points} ({100 * count_out_loop / num_points:.2f}%) are outside the pipe loop")
    if create_image:
        t1 = perf_counter()
        from PIL import Image, ImageDraw, ImageFont
        img_scale = 100
        off_x, off_y = ceil(img_scale / 1), ceil(img_scale / 1)
        img_scale_h = img_scale / 2
        text_height = ceil(img_scale * 3)
        line_height = ceil(text_height * (1 + 1 / 3))
        draw_text_off = ceil(img_scale / 2)
        bg = (0, 0, 0)
        fg = (255, 255, 255)
        pipe_network = (255, 0, 0)
        in_points = (0, 0, 255)
        out_points = (0, 127, 255)
        start_point_c = (127, 127, 127)
        furthest_point_c = (0, 255, 0)

        text_lines = [
            (f"Start: ({start[1]}, {start[0]})", start_point_c),
            (f"Furthest: ({furthest_point[1][1]}, {furthest_point[1][0]}). {furthest_point[0]} steps", furthest_point_c),
            (f"Loop length: {len(loop)}", fg),
            (f"{count_in_loop}/{num_points} ({100 * count_in_loop / num_points:.2f}%) are inside the pipe loop", in_points),
            (f"{count_out_loop}/{num_points} ({100 * count_out_loop / num_points:.2f}%) are outside the pipe loop",
             out_points)
        ]

        draw_size = ((x_bound[1] - x_bound[0] + 1) * img_scale, (y_bound[1] - y_bound[0] + 1) * img_scale)

        img_size = (
            draw_size[0] + off_x * 2,
            draw_size[1] + draw_text_off * 2 + len(text_lines) * line_height + off_y * 2
        )
        img = Image.new(mode="RGB", size=img_size, color=bg)
        img_draw = ImageDraw.Draw(img)
        for i, (y, x) in enumerate(loop):
            prev_point = loop[i - 1 if i >= 1 else -1]
            next_point = loop[i + 1 if i < len(loop) - 1 else 0]
            img_center = (x * img_scale + img_scale_h + off_x, y * img_scale + img_scale_h + off_y)
            # img_draw.point(img_center, fill=pipe_network)
            img_draw.line(xy=(img_center, img_center), fill=pipe_network, width=ceil(img_scale / 5))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if (y + dy, x + dx) in (prev_point, next_point):
                    img_draw.line(xy=(img_center, (img_center[0] + dx * img_scale_h, img_center[1] + dy * img_scale_h)),
                                  fill=pipe_network, width=ceil(img_scale / 5))
        for (y, x), is_in_out in in_out.items():
            c = in_points if is_in_out else out_points
            img_draw.rectangle(xy=(
                (x * img_scale + off_x, y * img_scale + off_y),
                (x * img_scale + img_scale + off_x, y * img_scale + img_scale + off_y)
            ),
                fill=c, outline=c, width=1)
        for (y, x), c in [(start, start_point_c), (furthest_point[1], furthest_point_c)]:
            img_draw.line(xy=(
                (x * img_scale + off_x, y * img_scale + off_y),
                (x * img_scale + img_scale + off_x, y * img_scale + img_scale + off_y)
            ),
                fill=c, width=ceil(img_scale / 5))
            img_draw.line(xy=(
                (x * img_scale + img_scale + off_x, y * img_scale + off_y),
                (x * img_scale + off_x, y * img_scale + img_scale + off_y)
            ),
                fill=c, width=ceil(img_scale / 5))

        ImageFont.load_default()
        font = ImageFont.truetype(font="arial.ttf", size=text_height)

        for i, (line, c) in enumerate(text_lines):
            x, y = (line_height + off_x, draw_size[1] + draw_text_off + line_height * i + off_y)
            img_draw.text(
                xy=(x, y), text=line, fill=c, font=font, stroke_width=ceil(img_scale / 15), stroke_fill=c, anchor="lt"
            )

        img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "pipe_network.png"))
        img.save(img_path, format="PNG")
        t2 = perf_counter()
        log(f"Image saved to {img_path}. Took {timedelta(seconds=t2 - t1)}")
    return count_in_loop
