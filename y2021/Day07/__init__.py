from typing import Any, Optional, List, Callable

import numpy as np
from AoC_Companion.Day import Day, TaskResult


class Day07(Day):

    def __init__(self, year: int):
        super().__init__(year)

    def pre_process_input(self, data: Any) -> Any:
        data: List[str] = super().pre_process_input(data=data)
        ret: np.ndarray = np.array([int(x) for x in data[0].split(",")], dtype=int)
        return ret

    def run_t1(self, data: np.ndarray) -> Optional[TaskResult]:
        return self._run(data=data)

    def run_t2(self, data: Any) -> Optional[TaskResult]:
        def f(t):
            return ((t + 1) * t) / 2

        return self._run(data=data, f=f)

    @staticmethod
    def _run(data: np.ndarray, f: Optional[Callable[[int], int]] = None):
        mi, ma = np.min(data), np.max(data)
        best = np.inf
        tar_pos = -1
        no_kernel = f is None
        if f is None:
            def f(x):
                return x
        for i in range(mi + 1, ma, 1):
            this = np.sum(f(np.abs(data - i)), dtype=int)
            if this < best:
                best = this
                tar_pos = i
        return TaskResult(best, log=[
            f"There are {data.shape[0]} craps helping. How nice",
            f"Using {'no' if no_kernel else 'a'} kernel to adjust values",
            f"Craps will go to target position {tar_pos}"
        ])
