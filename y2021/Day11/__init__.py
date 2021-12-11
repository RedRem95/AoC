from typing import Any, Optional, List, Tuple, Set

import numpy as np
from AoC_Companion.Day import Day, TaskResult


class Day11(Day):

    def __init__(self, year: int):
        super().__init__(year)

    def pre_process_input(self, data: Any) -> Any:
        data: List[str] = super().pre_process_input(data=data)
        data = [x for x in data if len(x) > 0]
        ret = np.array([[int(x) for x in y] for y in data])
        return ret

    def run_t1(self, data: np.ndarray) -> Optional[TaskResult]:
        data = data.copy()
        flashes = 0
        n = 100

        for _ in range(n):
            data = self._do_step(data=data)
            to_flash = data > 9
            flashes += np.sum(to_flash)
            data[to_flash] = 0

        log = [
            f"There are {np.product(data.shape)} octopuses in the area",
            f"After {n} iterations you were able to observe {flashes} flashes",
        ]

        return TaskResult(flashes, log=log)

    def run_t2(self, data: np.ndarray) -> Optional[TaskResult]:
        data = data.copy()
        flashes = 0
        k = 0
        while True:
            data = self._do_step(data=data)
            to_flash = data > 9
            flashes += np.sum(to_flash)
            k += 1
            if to_flash.all():
                break
            data[to_flash] = 0
        log = [
            f"There are {np.product(data.shape)} octopuses in the area",
            f"After {k} iterations and {flashes} flashes all are in sync",
        ]
        return TaskResult(k, log=log)

    @staticmethod
    def _do_step(data: np.ndarray) -> np.ndarray:
        data = data + 1
        already_flashed: Set[Tuple[int, int]] = set()
        while True:
            flash_points = [x for x in zip(*np.where(data > 9)) if x not in already_flashed]
            if len(flash_points) <= 0:
                break
            for i, j in flash_points:
                already_flashed.add((i, j))
                data[max(0, i - 1):min(data.shape[0], i + 2), max(0, j - 1):min(data.shape[1], j + 2)] += 1
        return data
