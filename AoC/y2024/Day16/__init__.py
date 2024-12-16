import os.path
from collections import defaultdict
from enum import Enum
from queue import PriorityQueue, Queue
from time import perf_counter
from typing import Callable, AnyStr, List, Tuple, Dict, Set

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor

from ..Day15 import tpl_add

if os.path.basename(os.path.dirname(os.path.dirname(__file__))).startswith("y"):
    _YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[len("y"):])
else:
    raise Exception()

if os.path.basename(os.path.dirname(__file__)).startswith("Day"):
    _DAY = int(os.path.basename(os.path.dirname(__file__))[len("Day"):])
else:
    raise Exception()


class MapElementStyle(Enum):
    WALL = "#"
    FINISH = "E"
    START = "S"
    NOTHING = "."


directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]


def get_next_direction(direction: Tuple[int, int]) -> List[Tuple[int, int]]:
    dir_idx = directions.index(direction)
    return [directions[dir_idx - 1], directions[(dir_idx + 1) % len(directions)]]


def search_path(maze: Dict[Tuple[int, int], MapElementStyle], log: Callable[[AnyStr], None]) -> Tuple[int, int]:
    x_min, y_min = min(x[1] for x in maze.keys()), min(x[0] for x in maze.keys())
    x_max, y_max = max(x[1] for x in maze.keys()), max(x[0] for x in maze.keys())
    log(f"Searching for best path in a {x_max - x_min}x{y_max - y_min} maze")
    starts = set(pos for pos, style in maze.items() if style == MapElementStyle.START)
    finishes = set(pos for pos, style in maze.items() if style == MapElementStyle.FINISH)
    start_direction = 0, 1
    not_passable = {MapElementStyle.WALL}
    if len(finishes) <= 0:
        raise Exception()

    if len(starts) != 1:
        raise Exception()

    start_pos = starts.pop()
    del starts

    log(f"The race starts at {start_pos[1]}, {start_pos[0]}")
    log(f"The race finishes at {' or '.join(f'{x[1]}, {x[0]}' for x in finishes)}")

    queue: PriorityQueue[Tuple[int, List[Tuple[int, int]], Tuple[int, int]]] = PriorityQueue()
    queue2: Queue[Tuple[Tuple[int, int], Tuple[int, int]]] = Queue()

    queue.put((0, [start_pos], start_direction))
    queue2.put((start_pos, start_direction))
    cost_map: Dict[Tuple[Tuple[int, int], Tuple[int, int]], int] = defaultdict(lambda: float("inf"))
    cost_map[(start_pos, start_direction)] = 0
    path_map: Dict[Tuple[Tuple[int, int], Tuple[int, int]], Set[Tuple[Tuple[int, int], Tuple[int, int]]]] = defaultdict(
        set)
    t1 = perf_counter()
    while not queue2.empty():
        cur_position, cur_direction = queue2.get()
        next_position = tpl_add(cur_position, cur_direction)
        if next_position in maze and maze[next_position] not in not_passable:
            if cost_map[(next_position, cur_direction)] == cost_map[(cur_position, cur_direction)] + 1:
                path_map[(next_position, cur_direction)].add((cur_position, cur_direction))
            elif cost_map[(next_position, cur_direction)] > cost_map[(cur_position, cur_direction)] + 1:
                cost_map[(next_position, cur_direction)] = cost_map[(cur_position, cur_direction)] + 1
                path_map[(next_position, cur_direction)] = {(cur_position, cur_direction)}
                queue2.put((next_position, cur_direction))
        for next_direction in get_next_direction(cur_direction):
            if cost_map[(cur_position, next_direction)] == cost_map[(cur_position, cur_direction)] + 1000:
                path_map[(cur_position, next_direction)].add((cur_position, cur_direction))
            elif cost_map[(cur_position, next_direction)] > cost_map[(cur_position, cur_direction)] + 1000:
                cost_map[(cur_position, next_direction)] = cost_map[(cur_position, cur_direction)] + 1000
                path_map[(cur_position, next_direction)] = {(cur_position, cur_direction)}
                queue2.put((cur_position, next_direction))
    t2 = perf_counter()
    log(f"Search for best path took {t2 - t1:.6}s")
    best_finish = sorted(finishes, key=lambda x: min(cost_map[(x, d)] for d in directions))[0]
    best_direction = sorted(((p, d) for p, d in cost_map.keys() if p == best_finish), key=lambda x: cost_map[x])[0][1]

    finish_tiles = set()
    queue_back: Queue[Tuple[Tuple[int, int], Tuple[int, int]]] = Queue()
    queue_back.put((best_finish, best_direction))
    t1 = perf_counter()
    while not queue_back.empty():
        cur_position, cur_direction = queue_back.get()
        finish_tiles.add(cur_position)
        for orig_position, orig_direction in path_map[(cur_position, cur_direction)]:
            queue_back.put((orig_position, orig_direction))
    t2 = perf_counter()
    log(f"Backtracking of all tiles adjacent to best paths took {t2 - t1:.6}s")

    return min(cost_map[(best_finish, d)] for d in directions), len(finish_tiles)


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    ret = {}
    for i, line in enumerate(x.strip() for x in data if len(x.strip()) > 0):
        for j, char in enumerate(line):
            ret[(i, j)] = MapElementStyle(char)

    return ret


@Task(year=2024, day=_DAY, task=1)
def task01(data, log: Callable[[AnyStr], None]):
    ret, path = search_path(data, log=log)
    log(f"It takes at least {ret} points to get to the finish")
    return ret


@Task(year=2024, day=_DAY, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    ret, good_tiles = search_path(data, log=log)
    log(f"There are {good_tiles} tiles adjacent to best path that would be good to sit at")
    return good_tiles
