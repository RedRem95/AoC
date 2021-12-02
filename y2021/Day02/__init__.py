from typing import Any, Optional
from time import time

import numpy as np


from AoC_Companion.Day import Day, TaskResult, StarTask


class Day02(Day):

    def pre_process_input(self, data: Any) -> Any:
        data = super().pre_process_input(data=data)
        return [x.split(" ")[:2] for x in data if len(x) > 0]

    def run_t1(self, data: Any) -> Optional[TaskResult]:
        t1 = time()
        pos = np.array([0, 0, 0])
        move = {
            "forward": np.array([1, 0, 1]),
            "up": np.array([0, -1, 1]),
            "down": np.array([0, 1, 1])
        }
        for t, v in data:
            pos += move[t] * int(v)
        log = [
            f"Ending position:   ({pos[0]}, {pos[1]})",
            f"Total units moved: {pos[2]}",
            f"Direct distance:   {np.sqrt(np.sum(np.square(pos[:2]))):.2f}"
        ]
        t2 = time()
        return TaskResult(result=str(np.prod(pos[:2])),
                          duration=t2 - t1,
                          log=log)

    def run_t2(self, data: Any) -> Optional[TaskResult]:
        t1 = time()
        pos = np.array([0, 0, 0, 0])
        move = {
            "forward": lambda: np.array([1, pos[-1], np.abs(pos[-1]), 0]),
            "up": lambda: np.array([0, 0, 0, -1]),
            "down": lambda: np.array([0, 0, 0, 1])
        }
        for t, v in data:
            pos += move[t]() * int(v)
        log = [
            f"Ending position:   ({pos[0]}, {pos[1]})",
            f"Ending aim:        {pos[-1]}",
            f"Total units moved: {pos[2]}",
            f"Direct distance:   {np.sqrt(np.sum(np.square(pos[:2]))):.2f}"
        ]
        t2 = time()
        return TaskResult(result=str(np.prod(pos[:2])),
                          duration=t2 - t1,
                          log=log)
