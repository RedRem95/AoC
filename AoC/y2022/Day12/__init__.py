from typing import Callable, AnyStr, Tuple, List, Optional, Union
from time import perf_counter

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


@Task(year=2022, day=12, task=1)
def task01(data: Tuple[np.ndarray, Tuple[int, int], Tuple[int, int]], log: Callable[[AnyStr], None]):
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

    return ret


@Task(year=2022, day=12, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    height_map, start, end = data
    log(f"Map-size: {height_map.shape[1]}x{height_map.shape[0]}; end: {end}")
    start_points: List[Tuple[int, int]] = [_create_idx(height_map, x) for x in (zip(*np.where(height_map == 0)))]
    log(f"Now considering {len(start_points)} starting points")

    prepared_map = _prepare_map(height_map=height_map)
    log(" -> Prepared map for routing")

    t1 = perf_counter()
    # noinspection PyTypeChecker
    dist_matrix, predecessors = shortest_path(
        prepared_map, directed=True, return_predecessors=True, indices=start_points
    )
    t2 = perf_counter()
    log(f" -> Route planned. Took {t2 - t1}s")

    ret = int(np.min(dist_matrix[:, _create_idx(height_map, end)]))
    best_start = np.where(dist_matrix[:, _create_idx(height_map, end)] == ret)[0][0]
    start = (best_start // height_map.shape[1], best_start % height_map.shape[1])
    log(f"Fastest route to get to {end} starts at {start} and takes {ret} steps")

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

