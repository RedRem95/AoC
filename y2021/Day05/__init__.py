from typing import Any, Optional, List, Iterable, Dict, Tuple

import numpy as np
from AoC_Companion.Day import Day, TaskResult


class Day05(Day):

    def pre_process_input(self, data: Any) -> Any:
        data: List[str] = super().pre_process_input(data=data)
        data = [x for x in data if len(x) > 0]
        ret = np.zeros((len(data), 4), dtype=int)
        for i, d in enumerate(data):
            p1, p2 = d.split("->")
            ret[i, 0] = int(p1.split(",")[0].strip())
            ret[i, 1] = int(p1.split(",")[1].strip())
            ret[i, 2] = int(p2.split(",")[0].strip())
            ret[i, 3] = int(p2.split(",")[1].strip())
        return ret

    def run_t1(self, data: Any) -> Optional[TaskResult]:
        return self._run(data=data[np.logical_or(data[:, 0] == data[:, 2], data[:, 1] == data[:, 3])])

    def run_t2(self, data: Any) -> Optional[TaskResult]:
        return self._run(data=data)

    @staticmethod
    def _run(data: np.ndarray) -> TaskResult:
        data: np.ndarray
        log = [
            f"There are matching {data.shape[0]} lines"
        ]
        collision_map: Dict[Tuple[int, int], int] = {}
        dangerous_points = 0
        for i in range(data.shape[0]):
            for pt in point_line(p1=data[i, :2], p2=data[i, 2:]):
                if pt not in collision_map:
                    collision_map[pt] = 0
                collision_map[pt] += 1
                if collision_map[pt] == 2:
                    dangerous_points += 1
        log.append(f"There are {dangerous_points} dangerous points")
        return TaskResult(dangerous_points, log=log)


def point_line(p1: np.ndarray, p2: np.ndarray) -> Iterable[Tuple[int, int]]:
    def _is_int(_x: float) -> bool:
        return int(_x) == _x

    if p1[0] != p2[0]:
        m = (p2[1] - p1[1]) / (p2[0] - p1[0])
    else:
        m = None

    if m is None:
        inc = -1 if p1[1] > p2[1] else 1
        for i in range(p1[1], p2[1] + inc, inc):
            yield p1[0], i
    else:
        inc = -1 if p1[0] > p2[0] else 1
        for i in range(p1[0], p2[0] + inc, inc):
            y = m * (i - p1[0]) + p1[1]
            if _is_int(y):
                yield i, int(y)
