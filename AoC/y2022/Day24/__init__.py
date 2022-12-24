from collections import defaultdict
from datetime import timedelta
from typing import Callable, AnyStr, List, Dict, Set, Tuple

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor

_BLIZZ_DIRECTIONS = {
    "^": (0, -1),
    "v": (0, 1),
    "<": (-1, 0),
    ">": (1, 0),
}

_MOVE_DIRECTIONS = [
    (0, -1),
    (0, 1),
    (0, 0),
    (1, 0),
    (-1, 0)
]

_T_VALLEY = Set[Tuple[int, int]]
_T_BLIZZARD = List[Tuple[Tuple[int, int], Tuple[int, int]]]
_T_DATA = Tuple[_T_VALLEY, _T_BLIZZARD]


@Preprocessor(year=2022, day=24)
def preproc_1(data: List[str]):
    valley: _T_VALLEY = set()
    blizzards: _T_BLIZZARD = []
    y = 0
    for line in data:
        line = line.strip()
        if len(line) <= 0:
            continue
        for x, c in enumerate(line):
            if c in _BLIZZ_DIRECTIONS:
                blizzards.append(((x, y), _BLIZZ_DIRECTIONS[c]))
            elif c == "#":
                valley.add((x, y))
            elif c == ".":
                pass
            else:
                raise Exception(f"{c} in {(x, y)}")
        y += 1
    return valley, blizzards


@Task(year=2022, day=24, task=1)
def task01(data: _T_DATA, log: Callable[[AnyStr], None]):
    min_y, max_y = min(x[1] for x in data[0]), max(x[1] for x in data[0])
    min_x, max_x = min(x[0] for x in data[0]), max(x[0] for x in data[0])
    log(f"Valley is {max_x - min_x + 1}x{max_y - min_y + 1} big")
    log(f"There are {len(data[1])} blizzards moving around")
    ret, _, start, finish = _sim_valley(valley=data[0], blizzards=data[1], start=None, finish=None)
    log(f"The expedition started at {start} and finished at {finish}")
    log(f"After {timedelta(minutes=ret)} the expedition reached the exit at {finish}")
    return ret


@Task(year=2022, day=24, task=2, extra_config={"num_tours": 3})
def task02(data, log: Callable[[AnyStr], None], num_tours: int):
    valley, blizzards = data
    min_y, max_y = min(x[1] for x in valley), max(x[1] for x in valley)
    min_x, max_x = min(x[0] for x in valley), max(x[0] for x in valley)
    log(f"Valley is {max_x - min_x + 1}x{max_y - min_y + 1} big")
    log(f"There are {len(blizzards)} blizzards moving around")
    start, finish, first_start = None, None, None
    ret = 0
    for i in range(num_tours):
        r, blizzards, finish, start = _sim_valley(
            valley=valley, blizzards=blizzards, start=start, finish=finish
        )
        if first_start is None:
            first_start = finish
        ret += r
        log(f"  -> {i + 1:{len(str(num_tours))}d}. tour from {finish} to {start} took {timedelta(minutes=r)}")
    log(f"The {num_tours} tours from {first_start} to {start} took {timedelta(minutes=ret)}")
    return ret


def _sim_valley(
        valley: _T_VALLEY, blizzards: _T_BLIZZARD, start: Tuple[int, int] = None, finish: Tuple[int, int] = None,
) -> Tuple[int, _T_BLIZZARD, Tuple[int, int], Tuple[int, int]]:
    min_y, max_y = min(x[1] for x in valley), max(x[1] for x in valley)
    min_x, max_x = min(x[0] for x in valley), max(x[0] for x in valley)
    min_max_valley = (min_x, max_x), (min_y, max_y)
    if start is None:
        y = min_y
        for x in range(min_x, max_x + 1, 1):
            pt = (x, y)
            if pt not in valley:
                start = pt
    if start in valley:
        raise Exception()
    if finish is None:
        y = max_y
        for x in range(min_x, max_x + 1, 1):
            pt = (x, y)
            if pt not in valley:
                finish = pt
    if finish in valley:
        raise Exception()
    for pt in [start, finish] + [x[0] for x in blizzards]:
        if not _check_in_valley(min_max_valley=min_max_valley, pt=pt):
            raise Exception()
    current_positions: Dict[Tuple[int, int], int] = {start: 0}

    i = 0

    while finish not in current_positions:
        i += 1
        new_blizzards: _T_BLIZZARD = []
        for blizz_pos, blizz_dir in blizzards:
            blizz_pos, blizz_dir = _next_blizzard(
                valley=valley, min_max_valley=min_max_valley, blizz_pos=blizz_pos, blizz_dir=blizz_dir
            )
            new_blizzards.append((blizz_pos, blizz_dir))
        blizzards = new_blizzards
        blizz_positions = set(x[0] for x in blizzards)
        proposed_movements = {}
        for pos, cost in current_positions.items():
            for pot_pos in (_tpl_add(t1=pos, t2=x) for x in _MOVE_DIRECTIONS):
                if pot_pos in valley:
                    continue
                if pot_pos in blizz_positions:
                    continue
                if not _check_in_valley(min_max_valley=min_max_valley, pt=pot_pos):
                    continue
                proposed_movements[pot_pos] = cost + 1
        # human_positions = sorted(new_human_positions, key=lambda x: _tpl_dist(t1=x, t2=finish))[:10000]
        current_positions = proposed_movements

    return current_positions[finish], blizzards, start, finish


def _check_in_valley(min_max_valley: Tuple[Tuple[int, int], Tuple[int, int]], pt: Tuple[int, int]):
    (min_x, max_x), (min_y, max_y) = min_max_valley
    return min_x <= pt[0] <= max_x and min_y <= pt[1] <= max_y


def _next_blizzard(
        valley: _T_VALLEY, min_max_valley: Tuple[Tuple[int, int], Tuple[int, int]],
        blizz_pos: Tuple[int, int], blizz_dir: Tuple[int, int],
) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    n = blizz_pos
    while True:
        n = _tpl_add(t1=n, t2=blizz_dir)
        if n in valley:
            pass
        elif not _check_in_valley(min_max_valley=min_max_valley, pt=n):
            n = {
                (0, -1): (blizz_pos[0], min_max_valley[1][1]),
                (0, 1): (blizz_pos[0], min_max_valley[1][0]),
                (-1, 0): (min_max_valley[0][1], blizz_pos[1]),
                (1, 0): (min_max_valley[0][0], blizz_pos[1]),
            }[blizz_dir]
        else:
            return n, blizz_dir


def _print_valley(valley: _T_VALLEY, blizzards: _T_BLIZZARD, cur_pos: Tuple[int, int] = None) -> str:
    min_y, max_y = min(x[1] for x in valley), max(x[1] for x in valley)
    min_x, max_x = min(x[0] for x in valley), max(x[0] for x in valley)

    blizzard_dict = defaultdict(list)
    for blizz_pos, blizz_dir in blizzards:
        blizzard_dict[blizz_pos].append(blizz_dir)

    ret = []
    for y in range(min_y, max_y + 1, 1):
        line = []
        for x in range(min_x, max_x + 1, 1):
            c = "."
            pt = (x, y)
            if pt in valley:
                c = "#"
            if pt in blizzard_dict:
                blizz_dirs = blizzard_dict[pt]
                if len(blizz_dirs) == 1:
                    c = [x for x, y in _BLIZZ_DIRECTIONS.items() if y == blizz_dirs[0]][0]
                else:
                    c = str(len(blizz_dirs))
            if cur_pos is not None and pt == cur_pos:
                c = "E"
            line.append(c)
        ret.append("".join(line))
    return "\n".join(ret)


def _tpl_add(t1: Tuple[int, int], t2: Tuple[int, int]) -> Tuple[int, int]:
    return t1[0] + t2[0], t1[1] + t2[1]
