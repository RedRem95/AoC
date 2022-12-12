from typing import Callable, AnyStr, Tuple, List, Optional, Union
from time import perf_counter
import os

import numpy as np
from scipy.sparse import coo_matrix as sparse_matrix
from scipy.sparse.csgraph import shortest_path, dijkstra

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022, day=12)
def preproc_1(data):
    ret = []
    start, end = None, None
    i = 0
    for line in data:
        line = line.strip()
        if len(line) <= 0:
            continue
        ret.append([])
        for j, c in enumerate(line):
            if str(c).isupper():
                if c == "S":
                    start = (i, j)
                    c = "a"
                if c == "E":
                    end = (i, j)
                    c = "z"
            if not c.islower():
                raise Exception()
            ret[-1].append(ord(c) - ord("a"))
        i += 1
    return np.array(ret), start, end


@Task(year=2022, day=12, task=1, extra_config={"draw": True})
def task01(data: Tuple[np.ndarray, Tuple[int, int], Tuple[int, int]], log: Callable[[AnyStr], None], draw: bool):
    height_map, start, end = data
    log(f"Map-size: {height_map.shape[1]}x{height_map.shape[0]}; start: {start}; end: {end}")

    prepared_map = _prepare_map(height_map=height_map)
    log(" -> Prepared map for routing")

    t1 = perf_counter()
    dist_matrix, predecessors = shortest_path(
        prepared_map, directed=True, return_predecessors=True, indices=_create_idx(height_map, start)
    )
    t2 = perf_counter()
    log(f" -> Route planned. Took {t2 - t1}s")
    ret = int(dist_matrix[_create_idx(height_map, end)])
    log(f"Fastest route to get from {start} to {end} is {ret} steps long")

    if draw:
        fig, _ = _create_map_image(
            height_map=height_map, predecessors=predecessors, start=_create_idx(height_map, start),
            end=_create_idx(height_map, end)
        )
        fig.savefig(os.path.join(os.path.dirname(__file__), f"p1.png"), dpi=600)

    return ret


@Task(year=2022, day=12, task=2, extra_config={"draw": True})
def task02(data: Tuple[np.ndarray, Tuple[int, int], Tuple[int, int]], log: Callable[[AnyStr], None], draw: bool):
    height_map, start, end = data
    log(f"Map-size: {height_map.shape[1]}x{height_map.shape[0]} ({np.prod(height_map.shape)}); end: {end}")
    start_points = [x for x in (zip(*np.where(height_map == 0)))]
    start_point_idx: List[int] = [_create_idx(height_map, x) for x in start_points]
    log(f"Now considering {len(start_point_idx)} starting points")

    prepared_map = _prepare_map(height_map=height_map)
    log(" -> Prepared map for routing")

    t1 = perf_counter()
    # noinspection PyTypeChecker
    dist_matrix, predecessors = shortest_path(
        prepared_map, directed=True, return_predecessors=True, indices=start_point_idx, unweighted=True,
    )
    t2 = perf_counter()
    log(f" -> Route planned. Took {t2 - t1}s")

    ret = int(np.min(dist_matrix[:, _create_idx(height_map, end)]))
    best_route = np.where(dist_matrix[:, _create_idx(height_map, end)] == ret)[0][0]
    start = start_points[best_route]
    log(f"Fastest route to get to {end} starts at {start} and takes {ret} steps")

    if draw:
        predecessors = predecessors[best_route] if len(start_point_idx) > 0 else predecessors
        fig, _ = _create_map_image(
            height_map=height_map, predecessors=predecessors, start=_create_idx(height_map, start),
            end=_create_idx(height_map, end)
        )
        fig.savefig(os.path.join(os.path.dirname(__file__), f"p2.png"), dpi=600)

    return ret


def _prepare_map(height_map: np.ndarray) -> Union[sparse_matrix, np.ndarray]:
    points = height_map.shape[0] * height_map.shape[1]
    min_pt = (0, 0)
    max_pt = (height_map.shape[0] - 1, height_map.shape[1] - 1)
    ret = np.zeros((points, points), dtype=int)
    for i in range(height_map.shape[0]):
        for j in range(height_map.shape[1]):
            pt = _create_idx(height_map, (i, j))
            current = (i, j)
            pot_points = _potential_steps(curr=current, min_pt=min_pt, max_pt=max_pt)
            for n in pot_points:
                if height_map[n] - 1 == height_map[current]:
                    ret[pt, _create_idx(height_map, n)] = 1
                elif height_map[n] == height_map[current]:
                    ret[pt, _create_idx(height_map, n)] = 1
                elif height_map[n] < height_map[current]:
                    ret[pt, _create_idx(height_map, n)] = 1
                else:
                    ret[pt, _create_idx(height_map, n)] = 0
    return ret


def _create_idx(height_map: np.ndarray, pt: Tuple[int, int]) -> int:
    return pt[0] * height_map.shape[1] + pt[1]


def _create_pt(height_map: np.ndarray, idx: int) -> Tuple[int, int]:
    return idx // height_map.shape[1], idx % height_map.shape[1]


def _potential_steps(curr: Tuple[int, int], min_pt: Tuple[int, int], max_pt: Tuple[int, int]) -> List[Tuple[int, int]]:
    ret = []

    if curr[0] > min_pt[0]:
        ret.append((curr[0] - 1, curr[1]))
    if curr[0] < max_pt[0]:
        ret.append((curr[0] + 1, curr[1]))
    if curr[1] > min_pt[1]:
        ret.append((curr[0], curr[1] - 1))
    if curr[1] < max_pt[1]:
        ret.append((curr[0], curr[1] + 1))

    return ret


def _create_map_image(height_map: np.ndarray, predecessors: np.ndarray, start: int, end: int) -> Tuple["Figure", "Axes"]:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    fig: plt.Figure
    ax: plt.Axes
    fig.set_size_inches(5, 5)
    ax.set_axis_off()
    fig.suptitle(f"Your route from {_create_pt(height_map, start)[::-1]} to {_create_pt(height_map, end)[::-1]}")

    img = np.zeros(height_map.shape, dtype=np.int64)
    img = height_map.copy()
    current = end
    i = 1

    while current != start:
        img[_create_pt(height_map, current)] = np.max(height_map) * 1.5
        current = predecessors[current]
        i += 1
        if current < 0:
            raise Exception()
    img[_create_pt(height_map, start)] = np.max(height_map) * 1.5
    # img[img == 0] = -i
    ax.imshow(img)

    return fig, ax

