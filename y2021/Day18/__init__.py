from itertools import permutations
from typing import Any, Optional, List

import numpy as np
from AoC_Companion.Day import Day, TaskResult

from .snail_math import SnailFishNumber


class Day18(Day):

    def __init__(self, year: int):
        super().__init__(year)

    def pre_process_input(self, data: Any) -> Any:
        data: List[str] = super().pre_process_input(data=data)
        data = [x for x in data if len(x) > 0]
        return data

    def run_t1(self, data: List[str]) -> Optional[TaskResult]:
        num = SnailFishNumber.parse(data=data[0])
        for line in data[1:]:
            num = SnailFishNumber.add(num, SnailFishNumber.parse(data=line))
        mag = num.get_magnitude()
        log = [
            f"Adding {len(data)} snailfish numbers resulted in:",
            str(num),
            f"with a magnitude of {mag}"
        ]
        return TaskResult(mag, log=log)

    def run_t2(self, data: np.ndarray) -> Optional[TaskResult]:
        snail_fish_numbers = [SnailFishNumber.parse(data=x) for x in data]
        combs = list(permutations(range(len(snail_fish_numbers)), 2))
        log = [f"Testing {len(combs)} combinations of {len(snail_fish_numbers)} snailfish numbers"]
        ret = 0
        best: List[SnailFishNumber] = []
        for i, j in combs:
            if i == j:
                continue
            n1 = snail_fish_numbers[i].copy()
            n2 = snail_fish_numbers[j].copy()
            a = SnailFishNumber.add(n1, n2)
            mag = a.get_magnitude()
            if mag > ret:
                best = [n1, n2, a]
                ret = mag

        log.extend([
            "By adding",
            f"{best[0]} +",
            f"{best[1]} =",
            f"{best[2]}",
            f"You get a maximum magnitude of {ret}"
        ])

        return TaskResult(ret, log=log)
