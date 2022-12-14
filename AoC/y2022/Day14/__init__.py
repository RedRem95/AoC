import os
from typing import Callable, AnyStr, Tuple, List, Set, Optional, Dict

import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor

_AIR = 0
_ROCK = 1
_SAND = 2
_START = 3

_COLORS = {
    _AIR: (0, 0, 0),
    _ROCK: (136, 140, 141),
    _SAND: (239, 221, 111),
    _START: (255, 0, 0),
}


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


@Task(year=2022, day=14, task=1, extra_config={"sand_start": (500, 0), "draw": False, "animate": False})
def task01(
        data: List[List[Tuple[int, int]]], log: Callable[[AnyStr], None], sand_start: Tuple[int, int], draw: bool,
        animate: bool
):
    rocks = _collect_rocks(all_lines=data)
    log(f"There are {len(rocks)} rocks, Sand flows from {sand_start} and cave has no bottom")
    collection, callback = _collect_callback(collect=draw and animate, sand_start=sand_start)
    cave = _sim_sand(rocks=rocks, sand_start=sand_start, bottom=False, callback=callback)
    sand = {k for k, v in cave.items() if v == _SAND}
    log(f"In the end there are {len(sand)} sand elements")

    if draw:
        cave[sand_start] = _START
        _draw(f_image=("task 1.final.png", cave), animation=("task 1.animation.mp4", collection))

    del collection
    return len(sand)


@Task(year=2022, day=14, task=2, extra_config={"sand_start": (500, 0), "draw": False, "animate": False})
def task02(
        data: List[List[Tuple[int, int]]], log: Callable[[AnyStr], None], sand_start: Tuple[int, int], draw: bool,
        animate: bool
):
    rocks = _collect_rocks(all_lines=data)
    abyss_start = max(x[1] for x in rocks)
    log(f"There are {len(rocks)} rocks, Sand flows from {sand_start}, cave has a bottom at {abyss_start + 2}")
    collection, callback = _collect_callback(collect=draw and animate, sand_start=sand_start)
    cave = _sim_sand(rocks=rocks, sand_start=(500, 0), bottom=True, callback=callback)
    sand = {k for k, v in cave.items() if v == _SAND}
    log(f"In the end there are {len(sand)} sand elements")

    if draw:
        cave[sand_start] = _START
        _draw(f_image=("task 2.final.png", cave), animation=("task 2.animation.mp4", collection))

    del collection
    return len(sand)


def _collect_callback(
        collect: bool, sand_start: Tuple[int, int]
) -> Tuple[List, Callable[[Dict[Tuple[int, int], int]], bool]]:
    collection = []
    if collect:
        def callback(_cave: Dict[Tuple[int, int], int]) -> bool:
            _cave = _cave.copy()
            _cave[sand_start] = _START
            collection.append(_cave)
            return True
    else:
        def callback(_cave: Dict[Tuple[int, int], int]) -> bool:
            return True
    return collection, callback


def _draw(
        f_image: Tuple[str, Dict[Tuple[int, int], int]], animation: Tuple[str, List[Dict[Tuple[int, int], int]]] = None
):
    try:
        import imageio as iio
        from tqdm import tqdm

        f_name, cave = f_image

        x_list, y_list = [x[0] for x in cave], [x[1] for x in cave]
        min_x, max_x, min_y, max_y = min(x_list), max(x_list), min(y_list), max(y_list)
        min_y = 0
        scale = 10

        img = _create_image(cave=cave, min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y)

        iio.imwrite(os.path.join(os.path.dirname(__file__), f_name), scale_image(img=img, scale=scale, block_size=1))

        if animation is not None and len(animation[1]) > 0:
            fps = 30
            block_size = 16
            scale = 5
            animation_name, animation_frames = animation
            gif_name = os.path.join(os.path.dirname(__file__), animation_name)

            with iio.get_writer(
                    gif_name, fps=fps, codec="libx264", quality=3, ffmpeg_log_level="quiet", macro_block_size=block_size
            ) as writer:
                img = None
                for frame in tqdm(animation_frames, desc="Writing Video", leave=False, unit="f"):
                    img = _create_image(cave=frame, min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y)
                    writer.append_data(scale_image(img=img, scale=scale, block_size=block_size))
                if img is not None:
                    for _ in range(fps):
                        writer.append_data(scale_image(img=img, scale=scale, block_size=block_size))

    except (ImportError, FileNotFoundError):
        pass


def _create_image(cave: Dict[Tuple[int, int], int], min_x: int, max_x: int, min_y: int,
                  max_y: int) -> np.ndarray:
    img = np.ones((max_y - min_y + 1, max_x - min_x + 1, 3), dtype=np.uint8)
    # for i in range(3):
    img[:, :, :] = _COLORS[_AIR][0]
    for pt, v in cave.items():
        img[pt[1] - min_y, pt[0] - min_x] = _COLORS[v]
    return img


def scale_image(img: np.ndarray, scale: int, block_size: int = 1) -> np.ndarray:
    from PIL import Image
    new_size = np.array(list(reversed(img.shape[:2]))) * scale
    new_size = block_size * np.ceil(new_size / block_size).astype(int)
    img = Image.fromarray(img)
    img = img.resize(size=new_size, resample=Image.NEAREST)
    img = np.array(img)
    return img


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


def _sim_sand(
        rocks: Set[Tuple[int, int]], sand_start: Tuple[int, int], bottom: bool,
        callback: Callable[[Dict[Tuple[int, int], int]], bool]
) -> Dict[Tuple[int, int], int]:
    cave: Dict[Tuple[int, int], int] = {k: _ROCK for k in rocks}

    abyss_start = max(x[1] for x in rocks)
    floor = abyss_start + 2 if bottom else -1

    while True:
        sand_current = sand_start
        while True:
            next_point = _next_sand(current=sand_current, cave=cave, floor=floor)
            if next_point is None:
                cave[sand_current] = _SAND
                if not callback(cave):
                    return cave
                if sand_current == sand_start:
                    return cave
                break
            if next_point[1] >= abyss_start and not bottom:
                return cave
            sand_current = next_point


def _next_sand(current: Tuple[int, int], cave: Dict[Tuple[int, int], int], floor: int) -> Optional[Tuple[int, int]]:
    next_sand = [(current[0], current[1] + 1), (current[0] - 1, current[1] + 1), (current[0] + 1, current[1] + 1)]
    for n in next_sand:
        if cave.get(n, _AIR) == _AIR and n[1] != floor:
            return n
    return None
