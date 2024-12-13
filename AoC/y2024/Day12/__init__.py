import os.path
from dataclasses import dataclass
from typing import Callable, AnyStr, List, Tuple

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor

from ..Day08 import tpl_add
from ..Day10 import _next_steps

if os.path.basename(os.path.dirname(__file__)).startswith("Day"):
    _DAY = int(os.path.basename(os.path.dirname(__file__))[len("Day"):])
else:
    raise Exception()


@dataclass
class GardenFieldType:
    plant: str
    fences: int = 0
    visited: bool = False


GARDEN_TYPE = List[List[GardenFieldType]]


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    ret = []
    for line in (x for x in data if len(x) > 0):
        ret.append([GardenFieldType(plant=x) for x in line])
    return ret


def propagate(seed: Tuple[int, int], garden: GARDEN_TYPE) -> List[Tuple[int, int]]:
    i, j = seed
    tile = garden[i][j]
    if tile.visited:
        return []
    tile.visited = True
    ret = [(i, j)]
    for i_next, j_next in _next_steps(pos=seed):
        if not (0 <= i_next < len(garden) and 0 <= j_next < len(garden[i])):
            tile.fences += 1
            continue
        tile_next = garden[i_next][j_next]
        if tile_next.plant == tile.plant:
            ret.extend(propagate((i_next, j_next), garden))
        else:
            tile.fences += 1
    return ret


def find_regions(garden: GARDEN_TYPE) -> List[List[Tuple[int, int]]]:
    ret = []

    for i in range(len(garden)):
        for j in range(len(garden[i])):
            if garden[i][j].visited:
                continue
            ret.append(propagate(seed=(i, j), garden=garden))
    return ret


def corner_count(pos: Tuple[int, int], garden: GARDEN_TYPE) -> int:
    def get_tile(_pos: Tuple[int, int]):
        if 0 <= _pos[0] < len(garden) and 0 <= _pos[1] < len(garden[_pos[0]]):
            return garden[_pos[0]][_pos[1]]
        return None

    me = get_tile(_pos=pos)

    def check_in(_tile: GardenFieldType):
        return _tile is not None

    def check_in_r(_tile: GardenFieldType):
        return check_in(_tile=_tile) and me.plant == _tile.plant

    n = get_tile(_pos=tpl_add(pos, (-1, 0)))
    ne = get_tile(_pos=tpl_add(pos, (-1, 1)))
    e = get_tile(_pos=tpl_add(pos, (0, 1)))
    se = get_tile(_pos=tpl_add(pos, (1, 1)))
    s = get_tile(_pos=tpl_add(pos, (1, 0)))
    sw = get_tile(_pos=tpl_add(pos, (1, -1)))
    w = get_tile(_pos=tpl_add(pos, (0, -1)))
    nw = get_tile(_pos=tpl_add(pos, (-1, -1)))

    neighbors = [n, e, s, w]
    neighbors_count = sum(1 if check_in_r(_tile=x) else 0 for x in neighbors)
    if neighbors_count == 0:
        return 4
    if neighbors_count == 1:
        return 2
    if neighbors_count in (2, 3, 4):
        ret = 0
        if neighbors_count == 2 and any(all(check_in_r(_tile=y) for y in x) for x in [(n, e), (e, s), (s, w), (w, n)]):
            ret = 1
        for x1, x2, x3 in [(n, e, ne), (e, s, se), (s, w, sw), (w, n, nw)]:
            if check_in_r(_tile=x1) and check_in_r(_tile=x2) and check_in(_tile=x3) and x3.plant != me.plant:
                ret += 1
        return ret
    raise Exception()


def count_corners(region: List[Tuple[int, int]], garden: GARDEN_TYPE) -> int:
    return sum(corner_count(pos=x, garden=garden) for x in region)


@Task(year=2024, day=_DAY, task=1)
def task01(data: GARDEN_TYPE, log: Callable[[AnyStr], None]):
    log(f"Working in a garden of {max(len(d) for d in data)}x{len(data)}")
    regions = find_regions(garden=data)
    log(f"Found {len(regions)} regions")
    ret = 0
    fences = 0
    for region in regions:
        region_size = len(region)
        fences = sum(data[i][j].fences for i, j in region)
        ret += region_size * fences
        fences += fences
    log(f"For the {len(regions)} regions you need {fences} fences. That will cost you {ret}")
    return ret


@Task(year=2024, day=_DAY, task=2)
def task02(data: GARDEN_TYPE, log: Callable[[AnyStr], None]):
    log(f"Working in a garden of {max(len(d) for d in data)}x{len(data)}")
    regions = find_regions(garden=data)
    log(f"Found {len(regions)} regions")
    ret = 0
    sides = 0
    tmpl = "A Region of {p} has an area of {rs} and {sc} sides => {rs}*{sc}={v}"
    for region in regions:
        region_size = len(region)
        side_count = count_corners(region=region, garden=data)
        plant = data[region[0][0]][region[0][1]].plant
        v = side_count * region_size
        if len(regions) < 10:
            log(tmpl.format(p=plant, rs=region_size, sc=side_count, v=v))
        ret += v
        sides += side_count
    log(f"Your areas have a total of {sides} sides")
    log(f"For the {len(regions)} regions you need a bulk order of fences. That will cost you {ret}")
    return ret
