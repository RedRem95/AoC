import os.path
from typing import Callable, AnyStr, Generator, Tuple, List

import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor
from scipy.sparse.csgraph import shortest_path
from tqdm import tqdm

from ..Day15.video_renderer import VideoRenderer
from ..Day16.image_renderer import draw_frame

if os.path.basename(os.path.dirname(os.path.dirname(__file__))).startswith("y"):
    _YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[len("y"):])
else:
    raise Exception()

if os.path.basename(os.path.dirname(__file__)).startswith("Day"):
    _DAY = int(os.path.basename(os.path.dirname(__file__))[len("Day"):])
else:
    raise Exception()


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    memory: List[Tuple[int, int]] = []
    for line in (x for x in data if len(x) > 0):
        x, y = line.split(",")
        memory.append((int(x), int(y)))
    return memory


def neighbors(pos: Tuple[int, int], bounds: Tuple[Tuple[int, int], Tuple[int, int]]) -> Generator[
    Tuple[int, int], Tuple[int, int], None]:
    for d in [(0, -1), (1, 0), (0, 1), (1, 0)]:
        ret = pos[0] + d[0], pos[1] + d[1]
        if all(bounds[i][0] <= ret[i] <= bounds[i][1] for i in range(len(bounds))):
            yield ret


def _get_idx(pos: Tuple[int, int], layout: int) -> int:
    return pos[0] * layout + pos[1]


def _revert_idx(idx: int, layout: int) -> Tuple[int, int]:
    return idx // layout, idx % layout


@Task(year=2024, day=_DAY, task=1, extra_config={"corruption": 1024})
def task01(data: List[Tuple[int, int]], log: Callable[[AnyStr], None], corruption: int):
    corrupt_memory = set(data[:corruption])
    min_x, max_x = min(x[0] for x in data), max(x[0] for x in data)
    min_y, max_y = min(x[1] for x in data), max(x[1] for x in data)
    width, height = max_x - min_x + 1, max_y - min_y + 1
    log(f"Memory layout has a size of {width}x{height}")
    log(f"Waiting until {len(corrupt_memory)} pieces of memory are corrupted")
    memory_layout = np.zeros((width * height, width * height), dtype=bool)
    for x in range(width):
        for y in range(height):
            xy = x, y
            if xy in corrupt_memory:
                continue
            for x_next, y_next in neighbors(xy, ((min_x, max_x), (min_y, max_y))):
                if (x_next, y_next) in corrupt_memory:
                    continue
                from_idx = _get_idx((x, y), width)
                to_idx = _get_idx((x_next, y_next), width)
                memory_layout[from_idx, to_idx] = True
                memory_layout[to_idx, from_idx] = True
    dist_matrix, predecessors = shortest_path(
        memory_layout, directed=False, return_predecessors=True, indices=0, unweighted=True,
    )
    ret = int(np.min(dist_matrix[_get_idx((max_x, max_y), width)]))
    log(f"The shortest path has a length of {ret}")
    return ret


@Task(year=2024, day=_DAY, task=2, extra_config={"render": False})
def task02(data: List[Tuple[int, int]], log: Callable[[AnyStr], None], render: bool):
    render_target = os.path.join(os.path.dirname(__file__), "p2.mp4") if render else None
    min_x, max_x = min(x[0] for x in data), max(x[0] for x in data)
    min_y, max_y = min(x[1] for x in data), max(x[1] for x in data)
    max_str_len = max([max(len(str(y)) for y in x) for x in data]), len(str(len(data)))
    width, height = max_x - min_x + 1, max_y - min_y + 1
    memory_layout = np.zeros((width * height, width * height), dtype=bool)
    log(f"Memory layout has a size of {width}x{height}")
    log(f"There are {len(data)} potential pieces of memory corrupt")
    log(f"Checking when the last piece of memory is corrupted that stops you from getting to the end")
    for x in range(width):
        for y in range(height):
            xy = x, y
            for x_next, y_next in neighbors(xy, ((min_x, max_x), (min_y, max_y))):
                from_idx = _get_idx((x, y), width)
                to_idx = _get_idx((x_next, y_next), width)
                memory_layout[from_idx, to_idx] = True
                memory_layout[to_idx, from_idx] = True

    corrupt_memory: List[Tuple[int, int]] = []
    path = []
    fps = 12

    bg_color = (0, 0, 0)
    path_color = (193, 176, 132)

    def _pixel_color(_path, _corrupt_memory, _width, _prev_path, _bg_color, _path_color, fade):
        from ..Day15 import tpl_add, tpl_mult
        _delta_color = tpl_add(_path_color, tpl_mult(_bg_color, (-1, -1, -1)))
        _path_color_new = tuple(int(x) for x in tpl_add(_bg_color, tpl_mult(_delta_color, (fade, fade, fade))))
        _path_color_old = tuple(
            int(x) for x in tpl_add(_bg_color, tpl_mult(_delta_color, (1 - fade, 1 - fade, 1 - fade))))

        def _fun(_idx: int):
            if _idx in _path and _idx in _prev_path:
                return _path_color
            if _idx in _path:
                return _path_color_new
            if fade != 1 and len(_corrupt_memory) > 0 and _revert_idx(_idx, _width) == _corrupt_memory[-1]:
                return 255, 0, 0
            if _revert_idx(_idx, _width) in _corrupt_memory:
                return 127, 131, 134
            if _idx in _prev_path:
                return _path_color_old
            return None

        return _fun

    with VideoRenderer(f_name=render_target, fps=fps, log=log, final_as_img=True) as renderer:
        with tqdm(desc="Letting memory become corrupted", leave=False, unit="corruptions") as pbar:
            while True:
                dist_matrix, predecessors = shortest_path(
                    memory_layout, directed=False, return_predecessors=True, indices=0, unweighted=True,
                )
                if dist_matrix[_get_idx((max_x, max_y), width)] >= np.inf:
                    ret = ",".join(str(x) for x in corrupt_memory[-1])
                    pbar.close()
                    log(f"When {ret} becomes corrupted you cant get to the end anymore. "
                        f"This happens when {len(corrupt_memory)} pieces of memory are corrupted")
                    return ret
                prev_path = list(path)
                path = [_get_idx((max_x, max_y), width)]
                while path[-1] != 0:
                    path.append(predecessors[path[-1]])
                if render:
                    for prc in np.linspace(0, 1, fps, True):
                        if len(corrupt_memory) > 0:
                            header = f"New Path around {','.join(f'{x:{max_str_len[0]}}' for x in corrupt_memory[-1])}"
                        else:
                            header = "Searching for initial path"
                        img = draw_frame(
                            pixel_size=12, size=(width, height),
                            header=header,
                            get_element=lambda _xy: _get_idx(_xy, width),
                            pixel_color=_pixel_color(path, corrupt_memory, width, prev_path, bg_color, path_color, prc),
                            bg_color=bg_color
                        )
                        renderer.add_frame(frame=img, scale=1)
                while True:
                    if len(data) <= 0:
                        pbar.close()
                        log("It is always possible to get to the end")
                        return "Not possible"
                    x, y = data.pop(0)
                    corrupt_memory.append((x, y))
                    corrupt_idx = _get_idx((x, y), width)
                    memory_layout[:, corrupt_idx] = False
                    memory_layout[corrupt_idx, :] = False
                    if render:
                        img = draw_frame(
                            pixel_size=12,
                            header=f"Corrupting {len(corrupt_memory):{max_str_len[1]}}: "
                                   f"{','.join(f'{x:{max_str_len[0]}}' for x in corrupt_memory[-1])}",
                            size=(width, height),
                            get_element=lambda _xy: _get_idx(_xy, width),
                            pixel_color=_pixel_color(path, corrupt_memory, width, [], bg_color, path_color, 1),
                            bg_color=bg_color
                        )
                        renderer.add_frame(frame=img, scale=1)
                    pbar.update(1)
                    if corrupt_idx in path:
                        break
