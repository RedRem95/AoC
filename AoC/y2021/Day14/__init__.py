from typing import Callable, AnyStr, List, Any, Optional, Dict, Tuple, Iterable, Set, Union
import os
import json
import enum
from queue import LifoQueue

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f_config_in:
    _config = json.load(f_config_in)


@Preprocessor(year=2021, day=14)
def pre_process_input(data: Any) -> Any:
    start = data[0].strip()
    rules: Dict[Tuple[str, str], str] = {}
    for line in (d for d in data[1:] if len(d) > 0):
        line1, line2 = line.split("->")
        rules[tuple(line1.strip())] = line2.strip()
    return start, rules


@Task(year=2021, day=14, task=1, extra_config=_config)
def run_t1(data: Tuple[str, Dict[Tuple[str, str], str]], log: Callable[[str], None], sim_steps: Dict[str, int]) -> Any:
    return _run(data=data, steps=sim_steps["1"], log=log)


@Task(year=2021, day=14, task=2, extra_config=_config)
def run_t2(data: Tuple[str, Dict[Tuple[str, str], str]], log: Callable[[str], None], sim_steps: Dict[str, int]) -> Any:
    return _run(data=data, steps=sim_steps["2"], log=log)


def _run(data: Any, steps: int, log: Callable[[str], None]) -> Any:
    log(f"Simulated polymer creation for {steps} steps")
    counts = _do_polymer(start=data[0], rules=data[1], steps=steps)
    log(f"In the end {len(counts)} elements are involved")
    log(f"Length of final polymer is {sum(counts.values())}")
    ret = max(counts.values()) - min(counts.values())
    return ret


def _do_polymer(start: str, rules: Dict[Tuple[str, str], str], steps: int) -> Dict[str, int]:
    combs: Dict[Tuple[str, str], int] = {}

    def inc_comb(_combs: Dict[Tuple[str, str], int], _comb: Tuple[str, str], _amount: int = 1):
        if _comb not in _combs:
            _combs[_comb] = 0
        _combs[_comb] += _amount

    for j in range(len(start) - 1):
        inc_comb(_combs=combs, _comb=(start[j], start[j + 1]))

    for i in range(steps):
        new_combs = {}
        for comb, amount in combs.items():
            if comb in rules:
                inc_comb(_combs=new_combs, _comb=(comb[0], rules[comb]), _amount=amount)
                inc_comb(_combs=new_combs, _comb=(rules[comb], comb[1]), _amount=amount)
        combs = new_combs

    counts: Dict[str, int] = {}

    for comb, amount in combs.items():
        if comb[0] not in counts:
            counts[comb[0]] = 0
        counts[comb[0]] += amount

    counts[start[-1]] += 1

    return counts
