from typing import Callable, AnyStr, Optional, Dict, List

import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2023, day=2)
def preproc_1(data):
    ret = {}
    for line in (x.strip() for x in data if len(x.strip()) > 0):
        g_id, g_data = [x.strip() for x in line.split(":")]
        g_id = int(g_id.split(" ")[-1])
        if g_id in ret:
            raise Exception()
        ret[g_id] = []
        for pull in g_data.split(";"):
            pull = pull.strip()
            ret[g_id].append({})
            for d in pull.split(","):
                d = d.strip()
                count, color = d.split(" ")
                if color.lower().strip() in ret[g_id][-1]:
                    raise Exception()
                ret[g_id][-1][color.lower().strip()] = int(count)
    return ret


@Task(year=2023, day=2, task=1, extra_config={"cube_counts": {"red": 12, "green": 13, "blue": 14}})
def task01(data: Dict[int, List[Dict[str, int]]], log: Callable[[AnyStr], None], cube_counts: Dict[str, int]):
    log(f"Testing {len(data)} games")
    valid_games = []
    for g_id, g_data in data.items():
        valid = True
        for pull in g_data:
            if not valid:
                break
            for color, count in pull.items():
                if count > cube_counts.get(color, 0):
                    valid = False
                    break
        if valid:
            valid_games.append(g_id)
    log(f"{len(valid_games)} games are valid ({100*len(valid_games)/len(data):6.2f}%)")
    s = sum(valid_games)
    log(f"Sum of valid game ids: {s}")
    return s


@Task(year=2023, day=2, task=2, extra_config={"cube_colors": ["red", "blue", "green"]})
def task02(data: Dict[int, List[Dict[str, int]]], log: Callable[[AnyStr], None], cube_colors: List[str]):
    log(f"Testing {len(data)} games")
    game_powers = {}
    for g_id, g_data in data.items():
        min_cubes = {x: 0 for x in cube_colors}
        for pull in g_data:
            for k in cube_colors:
                min_cubes[k] = max(min_cubes[k], pull.get(k, 0))
        game_powers[g_id] = np.prod(list(min_cubes.values()))
    log(f"Min game power: {min(game_powers.values())}; Max game power: {max(game_powers.values())}")
    s = sum(game_powers.values())
    log(f"Sum of all game powers: {s}")
    return s