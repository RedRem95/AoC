from time import time
from typing import Any, Optional

import numpy as np
from AoC_Companion.Day import Day, TaskResult, StarTask


class Day01(Day):

    def pre_process_input(self, data: Any) -> Any:
        data = super().pre_process_input(data=data)
        return np.array([int(x) for x in data if len(x) > 0], dtype=np.int32)

    def run_t1(self, data: Any) -> Optional[TaskResult]:
        t1 = time()
        res = self._count_inc(data[:-1], data[1:])
        t2 = time()
        return TaskResult(day=self, task=StarTask.Task01,
                          result=str(res),
                          duration=t2 - t1,
                          log=[f"There are {len(data)} measurements"])

    def run_t2(self, data: Any) -> Optional[TaskResult]:
        data: np.ndarray
        t1 = time()
        window_size = 3
        res = 0
        for i in range(window_size + 1, data.shape[0] + 1):
            res += 1 if data[i - window_size - 1:i - 1].sum() < data[i - window_size:i].sum() else 0
        t2 = time()
        return TaskResult(day=self, task=StarTask.Task02,
                          result=str(res),
                          duration=t2 - t1,
                          log=[f"There are {len(data)} measurements"])

    @staticmethod
    def _count_inc(data1: np.ndarray, data2: np.ndarray):
        return np.sum(data1 < data2)
