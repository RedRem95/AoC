import enum
import queue
from typing import Any, Optional, List, Tuple, Dict, Callable

import numpy as np
from AoC_Companion.Day import Day, TaskResult


class Day10(Day):

    def __init__(self, year: int):
        super().__init__(year)

    def pre_process_input(self, data: Any) -> Any:
        data: List[str] = super().pre_process_input(data=data)
        data = [x for x in data if len(x) > 0]
        return data

    def run_t1(self, data: List[str]) -> Optional[TaskResult]:

        pts = {
            ")": 3,
            "]": 57,
            "}": 1197,
            ">": 25137
        }
        log = []
        ret = self._run(data=data, pts=pts, status=self.MachineStatus.Broken, log=log)
        ret = sum(ret)
        log.append(f"Syntax error score: {ret}")
        return TaskResult(ret, log=log)

    def run_t2(self, data: List[str]) -> Optional[TaskResult]:

        pts = {
            ")": 1,
            "]": 2,
            "}": 3,
            ">": 4
        }
        log = []
        ret = self._run(
            data=data, pts=pts, kernel=lambda x, y: x * 5 + y, status=self.MachineStatus.Incomplete, log=log
        )
        ret = int(np.median(ret))
        log.append(f"Autocomplete score: {ret}")
        return TaskResult(ret, log=log)

    def _run(self, data: List[str], pts: Dict[str, int], status: "MachineStatus",
             kernel: Callable[[int, int], int] = None, log: List[str] = None) -> List[int]:
        if log is None:
            def p(*_line: str):
                pass
        else:
            def p(*_line: str):
                log.extend(_line)
        p(f"Searching for lines that are {status.name}")
        if kernel is None:
            def kernel(x1: int, x2: int):
                return x1 + x2

            p(f"Using default addition kernel for scoring")
        matches = self.default_matches()
        ret = []
        p(f"Processing {len(data)} lines of code")
        for line in data:
            line_status, line_data = self.check_machine(line, matches=matches)
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

    @staticmethod
    def default_matches() -> Dict[str, str]:
        return {
            "(": ")",
            "{": "}",
            "[": "]",
            "<": ">"
        }

    @staticmethod
    def check_machine(code: str, matches: Dict[str, str] = None) -> Tuple[MachineStatus, Tuple[str, ...]]:
        if matches is None:
            matches = Day10.default_matches()
        machine = queue.LifoQueue()
        for x in code:
            if x in matches:
                machine.put(x)
            else:
                got = machine.get()
                if x != matches[got]:
                    return Day10.MachineStatus.Broken, (x,)
        if not machine.empty():
            ret = []
            while not machine.empty():
                ret.append(matches[machine.get()])
            return Day10.MachineStatus.Incomplete, tuple(ret)

        return Day10.MachineStatus.Valid, tuple()
