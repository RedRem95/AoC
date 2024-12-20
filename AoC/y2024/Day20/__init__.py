import os.path
from typing import Callable, AnyStr, Tuple, Dict

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor

from ..Day15 import tpl_add
from ..Day16 import MapElementStyle, directions

if os.path.basename(os.path.dirname(os.path.dirname(__file__))).startswith("y"):
    _YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[len("y"):])
else:
    raise Exception()

if os.path.basename(os.path.dirname(__file__)).startswith("Day"):
    _DAY = int(os.path.basename(os.path.dirname(__file__))[len("Day"):])
else:
    raise Exception()

NOT_PASSABLE = {MapElementStyle.WALL, }


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    maze = {}
    for i, line in enumerate(x for x in data if len(x) > 0):
        for j, column in enumerate(line):
            maze[(i, j)] = MapElementStyle(column)
    return maze


def get_cheat_targets(pt: Tuple[int, int], cheat_duration: int):
    for i in range(0, cheat_duration + 1, 1):
        w = cheat_duration - i
        for j in range(0, w + 1, 1):
            yield tpl_add(pt, (+i, +j)), i + j
            yield tpl_add(pt, (-i, +j)), i + j
            yield tpl_add(pt, (+i, -j)), i + j
            yield tpl_add(pt, (-i, -j)), i + j


def find_cheats(
        track: Dict[Tuple[int, int], MapElementStyle], cheat_duration: int,
        log: Callable[[AnyStr], None]
):
    start_position = [pos for pos, typ in track.items() if typ == MapElementStyle.START][0]
    finish_position = [pos for pos, typ in track.items() if typ == MapElementStyle.FINISH][0]
    log(f"Race goes from {start_position[0]};{start_position[1]} to {finish_position[0]};{finish_position[1]}")
    cur_pos = start_position
    point_length = {start_position: 0}
    i = 0
    while cur_pos != finish_position:
        neighbors = (tpl_add(cur_pos, d) for d in directions)
        neighbors = [x for x in neighbors if x in track and track[x] not in NOT_PASSABLE and x not in point_length]
        if len(neighbors) != 1:
            log(f"Race track is not unique. Found {len(neighbors)} potential next steps from {cur_pos}")
            return None
        i += 1
        cur_pos = neighbors[0]
        point_length[cur_pos] = i

    log(f"Race-track has a length of {len(point_length)}")
    log(f"Searching for cheats of a maximum length of {cheat_duration}")
    items = point_length.items()
    if cheat_duration > 3:
        try:
            from tqdm import tqdm
            items = tqdm(items, desc="Searching for ways to cheat", unit="points", leave=False)
        except:
            pass

    cheats_found = {}
    for pt, dist in items:
        for cheat_target, cheat_dist in set(get_cheat_targets(pt=pt, cheat_duration=cheat_duration)):
            if cheat_target == pt or cheat_target not in point_length:
                continue
            cheat_saves = point_length[cheat_target] - dist - cheat_dist
            if cheat_saves > 0:
                cheats_found[(pt, cheat_target)] = cheat_saves
    best_worst = sorted(cheats_found.items(), key=lambda x: x[1])
    (worst_from, worst_to), worst_save = best_worst[0]
    (best_from, best_to), best_save = best_worst[-1]
    log(f"Found {len(cheats_found)} possible cheats that would save some time.")
    log(f"Worst cheat goes from {worst_from[0]};{worst_from[1]} to {worst_to[0]};{worst_to[1]} and saves {worst_save}")
    log(f"Best  cheat goes from {best_from[0]};{best_from[1]} to {best_to[0]};{best_to[1]} and saves {best_save}")
    return cheats_found


@Task(year=2024, day=_DAY, task=1)
def task01(data, log: Callable[[AnyStr], None]):
    cheats = find_cheats(track=data, cheat_duration=2, log=log)
    return sum(1 if v >= 100 else 0 for v in cheats.values())


@Task(year=2024, day=_DAY, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    cheats = find_cheats(track=data, cheat_duration=20, log=log)
    return sum(1 if v >= 100 else 0 for v in cheats.values())
