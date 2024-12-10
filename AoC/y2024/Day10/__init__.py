import os.path
from typing import Callable, AnyStr, List, Tuple, Set, Optional

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor

if os.path.basename(os.path.dirname(__file__)).startswith("Day"):
    _DAY = int(os.path.basename(os.path.dirname(__file__))[len("Day"):])
else:
    raise Exception()


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    ret = []
    for line in (x for x in data if len(x) > 0):
        ret.append([None if y == "." else int(y) for y in line])
    return ret


def _next_steps(pos: Tuple[int, int]):
    y, x = pos
    return [(y - 1, x + 0), (y - 0, x + 1), (y + 1, x + 0), (y + 0, x - 1)]


def get_trail(pos: List[Tuple[int, int]], topo_map: List[List[Optional[int]]], target_height: int) -> Set[
    Tuple[Tuple[int, int], ...]]:
    if not (0 <= pos[-1][0] < len(topo_map) and 0 <= pos[-1][1] < len(topo_map[pos[-1][0]])):
        return set()
    current_tile = topo_map[pos[-1][0]][pos[-1][1]]
    if current_tile == target_height:
        return {tuple(pos)}
    if current_tile is None:
        return set()
    ret = set()
    for step in _next_steps(pos[-1]):
        if 0 <= step[0] < len(topo_map) and 0 <= step[1] < len(topo_map[step[0]]):
            if topo_map[step[0]][step[1]] == current_tile + 1:
                ret = ret.union(get_trail(pos + [step], topo_map, target_height))
    return ret


def get_trails(topo_map: List[List[Optional[int]]], starting_height: int, target_height: int) -> List[
    Set[Tuple[Tuple[int, int], ...]]]:
    ret = []
    for i in range(len(topo_map)):
        for j in range(len(topo_map[i])):
            if topo_map[i][j] == starting_height:
                ret.append(get_trail([(i, j)], topo_map, target_height))
    return ret


@Task(year=2024, day=_DAY, task=1, extra_config={"starting_height": 0, "target_height": 9})
def task01(data: List[List[Optional[int]]], log: Callable[[AnyStr], None], starting_height: int, target_height: int):
    log(f"Your hiking area has a size of {max(len(x) for x in data)}x{len(data)}")
    log(f"You are searching for unique {target_height}-height Points "
        f"starting from trailheads with a height of {starting_height}")
    starting_trails = get_trails(data, starting_height, target_height)
    log(f"There are {len(starting_trails)} points you could start your trail from")
    unique_ends_per_trails = [set(y[-1] for y in x) for x in starting_trails]
    ret = sum(len(x) for x in unique_ends_per_trails)
    log(f"The sum of all unique {target_height}-height Points you can reach per trailhead is {ret}")
    return ret


@Task(year=2024, day=_DAY, task=2, extra_config={"starting_height": 0, "target_height": 9})
def task02(data: List[List[Optional[int]]], log: Callable[[AnyStr], None], starting_height: int, target_height: int):
    log(f"Your hiking area has a size of {max(len(x) for x in data)}x{len(data)}")
    log(f"You are searching for unique trails that start from a trailheads with a height of {starting_height} "
        f"and lead to a {target_height}-height Point ")
    starting_trails = get_trails(data, starting_height, target_height)
    ret = sum(len(x) for x in starting_trails)
    log(f"There are {len(starting_trails)} points you could start your trail from and {ret} unique trails you can take")
    return ret
