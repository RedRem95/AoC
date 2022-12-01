from typing import Callable, AnyStr, List, Any, Optional, Dict, Tuple, Iterable, Set
import os
import json
import enum
from queue import LifoQueue

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2021, day=12)
def pre_process_input(data: Any) -> Any:
    data = [x for x in data if len(x) > 0]
    ret: Dict[str, Set[str]] = {}
    for line in data:
        line = line.strip()
        l1, l2 = line.split("-")
        if l1 not in ret:
            ret[l1] = set()
        if l2 not in ret:
            ret[l2] = set()
        ret[l1].add(l2)
        ret[l2].add(l1)
    return ret


@Task(year=2021, day=12, task=1)
def run_t1(data: Dict[str, Set[str]], log: Callable[[str], None]) -> Any:
    log(f"The tunnel network has {len(data)} caves")
    log(f"  {sum(1 if str(x).isupper() else 0 for x in data.keys() if x not in ('start', 'end'))} are big")
    log(f"  {sum(0 if str(x).isupper() else 1 for x in data.keys() if x not in ('start', 'end'))} are small")
    paths = _find_way(system=data, start="start", target="end", special_rule=False)
    log(f"There are {len(paths)} paths possible when you visit small caves only once")
    return len(paths)


@Task(year=2021, day=12, task=2)
def run_t2(data: Dict[str, Set[str]], log: Callable[[str], Any]) -> Any:
    log(f"The tunnel network has {len(data)} caves")
    log(f"  {sum(1 if str(x).isupper() else 0 for x in data.keys() if x not in ('start', 'end'))} are big")
    log(f"  {sum(0 if str(x).isupper() else 1 for x in data.keys() if x not in ('start', 'end'))} are small")
    paths = _find_way(system=data, start="start", target="end", special_rule=True)
    log(f"There are {len(paths)} paths possible when you allow yourself to visit one small cave twice")
    return len(paths)


def _can_visit(cave: str, visited: List[str]) -> bool:
    return cave.isupper() or cave not in visited


def _can_visit_special(cave: str, visited: List[str]) -> Tuple[bool, bool]:
    if _can_visit(cave=cave, visited=visited):
        return True, False
    lower_caves = [x for x in visited if x.islower()]
    if len(set(lower_caves)) == len(lower_caves) and cave not in ["start", "end"]:
        return True, True
    return False, False


def _find_way(system: Dict[str, Set[str]], start: str, target: str, special_rule: bool) -> Set[Tuple[str]]:
    import queue
    sub_paths = queue.Queue()
    sub_paths.put(([start], not special_rule))
    ret: Set[Tuple[str]] = set()

    while not sub_paths.empty():
        sub_path, special_taken = sub_paths.get()
        sub_path: List[str]
        special_taken: bool
        for next_cave in system[sub_path[-1]]:
            _special_taken = special_taken
            if _special_taken and not _can_visit(cave=next_cave, visited=sub_path):
                continue
            elif not _special_taken:
                can_visit, _special_taken = _can_visit_special(cave=next_cave, visited=sub_path)
                if not can_visit:
                    continue
            new_path = sub_path + [next_cave]
            if next_cave == target:
                ret.add(tuple(new_path))
            else:
                sub_paths.put((new_path, _special_taken))

    return ret
