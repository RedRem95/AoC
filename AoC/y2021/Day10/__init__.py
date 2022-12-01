from typing import Callable, AnyStr, List, Any, Optional, Dict, Tuple, Iterable
import os
import json
import enum
from queue import LifoQueue

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2021, day=10)
def pre_process_input(data: Any) -> Any:
    data = [x for x in data if len(x) > 0]
    return data


@Task(year=2021, day=10, task=1)
def run_t1(data: List[str], log: Callable[[AnyStr], None]) -> Any:

    pts = {
        ")": 3,
        "]": 57,
        "}": 1197,
        ">": 25137
    }
    ret = _run(data=data, pts=pts, status=MachineStatus.Broken, log=log)
    ret = sum(ret)
    log(f"Syntax error score: {ret}")
    return ret


@Task(year=2021, day=10, task=2)
def run_t2(data: List[str], log: Callable[[AnyStr], None]) -> Any:

    pts = {
        ")": 1,
        "]": 2,
        "}": 3,
        ">": 4
    }
    ret = _run(data=data, pts=pts, kernel=lambda x, y: x * 5 + y, status=MachineStatus.Incomplete, log=log)
    ret = int(np.median(ret))
    log(f"Autocomplete score: {ret}")
    return ret


def _run(data: List[str], pts: Dict[str, int], status: "MachineStatus",
         kernel: Callable[[int, int], int] = None, log: Callable[[AnyStr], None] = None) -> List[int]:
    if log is None:
        def p(*_line: str):
            pass
    else:
        def p(*_line: str):
            for _l in _line:
                log(_l)
    p(f"Searching for lines that are {status.name}")
    if kernel is None:
        def kernel(x1: int, x2: int):
            return x1 + x2

        p(f"Using default addition kernel for scoring")
    matches = default_matches()
    ret = []
    p(f"Processing {len(data)} lines of code")
    for line in data:
        line_status, line_data = check_machine(line, matches=matches)
        if line_status == status:
            line_score = 0
            for d in line_data:
                line_score = kernel(line_score, pts[d])
            ret.append(line_score)
    p(f"Found {len(ret)} lines of code that were {status.name} and matched")
    return ret


class MachineStatus(enum.Enum):
    Valid = 0
    Incomplete = 1
    Broken = 2


def default_matches() -> Dict[str, str]:
    return {
        "(": ")",
        "{": "}",
        "[": "]",
        "<": ">"
    }


def check_machine(code: str, matches: Dict[str, str] = None) -> Tuple[MachineStatus, Tuple[str, ...]]:
    if matches is None:
        matches = default_matches()
    machine = LifoQueue()
    for x in code:
        if x in matches:
            machine.put(x)
        else:
            got = machine.get()
            if x != matches[got]:
                return MachineStatus.Broken, (x,)
    if not machine.empty():
        ret = []
        while not machine.empty():
            ret.append(matches[machine.get()])
        return MachineStatus.Incomplete, tuple(ret)

    return MachineStatus.Valid, tuple()
