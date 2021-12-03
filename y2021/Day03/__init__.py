from typing import Any, Optional, List
from time import time

import numpy as np


from AoC_Companion.Day import Day, TaskResult, StarTask


class Day03(Day):

    def pre_process_input(self, data: Any) -> Any:
        data = super().pre_process_input(data=data)
        data = [[int(y) for y in x] for x in data if len(x) > 0]
        return np.array(data, dtype=np.int32)

    def run_t1(self, data: Any) -> Optional[TaskResult]:
        t1 = time()
        gamma = self.find_most_common(data=data)
        eps = self.find_least_common(data=data)
        log = [
            f"Log has {data.shape[0]} lines. Every line has {data.shape[1]} values",
            f"Extraction from log:",
            f"  Gamma: {''.join(str(x) for x in gamma)}",
            f"  Eps  : {''.join(str(x) for x in eps)}"
        ]
        gamma = self.bin_to_int(data=gamma)
        eps = self.bin_to_int(data=eps)
        power = gamma * eps
        log.extend([
            f"Converted to decimal:",
            f"  Gamma: {gamma}",
            f"  Eps  : {eps}",
            f"Resulting calculation:",
            f"  Power: {gamma * eps=}"
        ])
        t2 = time()
        return TaskResult(result=str(power),
                          duration=t2 - t1,
                          log=log)

    def run_t2(self, data: Any) -> Optional[TaskResult]:
        t1 = time()
        data: np.ndarray
        oxygen = data.copy()
        for i in range(data.shape[1]):
            common = self.find_most_common(data=oxygen)
            oxygen = oxygen[oxygen[:, i] == common[i], :]
            if oxygen.shape[0] == 1:
                break
        co2 = data.copy()
        for i in range(data.shape[1]):
            common = self.find_least_common(data=co2)
            co2 = co2[co2[:, i] == common[i], :]
            if co2.shape[0] == 1:
                break
        oxygen = oxygen[0]
        co2 = co2[0]
        log = [
            f"Log has {data.shape[0]} lines. Every line has {data.shape[1]} values",
            f"Extraction from log:",
            f"  Oxygen      : {''.join(str(x) for x in oxygen)}",
            f"  CO2         : {''.join(str(x) for x in co2)}"
        ]
        oxygen = self.bin_to_int(data=oxygen)
        co2 = self.bin_to_int(data=co2)
        life_support = oxygen * co2
        log.extend([
            f"Converted to decimal:",
            f"  Oxygen      : {oxygen}",
            f"  CO2         : {co2}",
            f"Resulting calculation:",
            f"  Life Support: {oxygen * co2=}"
        ])
        t2 = time()
        return TaskResult(result=str(life_support),
                          duration=t2 - t1,
                          log=log)

    @staticmethod
    def find_most_common(data: np.ndarray) -> np.ndarray:
        return (np.mean(data, axis=0) + 0.5).astype(int)

    @staticmethod
    def find_least_common(data: np.ndarray) -> np.ndarray:
        common = Day03.find_most_common(data=data)
        ret = np.zeros_like(common)
        ret[common == 0] = 1
        return ret

    @staticmethod
    def bin_to_int(data: np.ndarray) -> int:
        return int("".join([str(x) for x in data]), 2)
