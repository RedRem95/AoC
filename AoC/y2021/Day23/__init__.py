from typing import Callable, AnyStr, List, Any, Optional, Dict, Tuple, Iterable, Set, Union, Iterator
import os
import json
import enum
import queue
import itertools
from queue import LifoQueue
from itertools import permutations
from functools import lru_cache
from collections import Counter

import numpy as np
from scipy.spatial import distance
from scipy.signal import convolve2d
import matplotlib
import matplotlib.pyplot as plt

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

from .building import Hallway, Amphipod, AmphipodTypes, Room, State


with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f_in:
    _config: Dict[str, Dict[str, str]] = json.load(f_in)
    _longer_rooms = {int(k): list(Amphipod.parse_from_str(data=v)) for k, v in _config["longer_rooms"].items()}


@Preprocessor(year=2021, day=23)
def pre_process_input(data: Any) -> Any:
    data: List[str] = [x for x in data if len(x) > 0]
    hallway_len = 0
    i = data[1].index(".")
    for j in range(i, len(data[1])):
        if data[1][i] == ".":
            hallway_len += 1
            continue
        break
    room_stuff: Dict[int, List[Amphipod]] = {}
    for line in data[2:]:
        for j, c in enumerate(line[1:]):
            typ = AmphipodTypes.get_by_value(v=c)
            if typ is not None:
                if j not in room_stuff:
                    room_stuff[j] = []
                room_stuff[j].append(Amphipod(typ=typ))
    hallway = Hallway(size=hallway_len-1)
    for j, (idx, room) in enumerate(sorted(room_stuff.items(), key=lambda x: x[0])):
        room = Room(occupant=AmphipodTypes.get_by_idx(j), initial=list(reversed(room)))
        hallway.set_room(room=room, idx=idx)
    return hallway


@Task(year=2021, day=23, task=1)
def run_t1(data: Hallway, log: Callable[[str], None]) -> Any:
    return _run(data=data, log=log)


@Task(year=2021, day=23, task=2, extra_config={"longer_rooms": _longer_rooms})
def run_t2(data: Hallway, log: Callable[[str], None], longer_rooms: Dict[int, List[Amphipod]]) -> Any:
    for i, (_, room) in enumerate(data.get_rooms()):
        room.insert(1, longer_rooms[i])
    return _run(data=data, log=log)


def _run(data: Hallway, log: Callable[[str], None]) -> Any:
    state = State(hallway=data)
    solve_energy, solved_hallway = State.solve(init_state=state)
    log("From:")
    for s in str(data).split("\n"):
        log(s)
    log("")
    log(f"To (Used Energy: {solve_energy}):")
    for s in str(solved_hallway).split("\n"):
        log(s)
    return solve_energy
