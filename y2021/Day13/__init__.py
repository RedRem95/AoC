from typing import Any, Optional, List, Set, Tuple, Union

import numpy as np
from AoC_Companion.Day import Day, TaskResult


class Day13(Day):

    def __init__(self, year: int):
        super().__init__(year)

    def pre_process_input(self, data: Any) -> Any:
        data: List[str] = super().pre_process_input(data=data)
        ret: Set[Tuple[int, int]] = set()
        folds: List[Tuple[str, int]] = []
        k = 0
        for k, line in enumerate(data):
            if len(line) <= 0:
                break
            a, b = line.split(",")
            ret.add((int(a), int(b)))
        ret2 = np.zeros((max(x[1] for x in ret) + 1, max(x[0] for x in ret) + 1), dtype=bool)
        for j, i in ret:
            ret2[i, j] = True
        for line in data[k + 1:]:
            if len(line) <= 0:
                break
            line1, line2 = line.strip().split(" ")[-1].split("=")
            folds.append((line1, int(line2)))
        return ret2, folds

    def run_t1(self, data: Tuple[np.ndarray, List[Tuple[str, int]]]) -> Optional[TaskResult]:
        after_fold, folds = self.do_folds(data=data[0], folds=data[1], amount=1)
        ret = np.sum(after_fold)
        return TaskResult(ret, log=[f"After 1 fold {ret} dots are visible"])

    def run_t2(self, data: Tuple[np.ndarray, List[Tuple[str, int]]]) -> Optional[TaskResult]:
        after_fold, folds = self.do_folds(data=data[0], folds=data[1])
        log = [[]]
        for i in range(after_fold.shape[0]):
            for j in range(after_fold.shape[1]):
                if after_fold[i, j] == 1:
                    log[-1].append("#")
                else:
                    log[-1].append(" ")
            log.append([])
        return TaskResult("See below in log",
                          log=[f"After {folds} folds {np.sum(after_fold)} dots are visible",
                               *["".join(x for x in y) for y in log]])

    @staticmethod
    def do_folds(
            data: np.ndarray, folds: List[Tuple[str, int]], amount: Union[int, float] = None
    ) -> Tuple[np.ndarray, int]:
        if amount is None:
            amount = np.inf
        amount = min(amount, len(folds))

        ret = data

        i = 0
        while i < amount:
            fold = folds[i]
            if fold[0] == "x":
                ret = np.transpose(ret)
            upper = ret[:fold[1], :]
            lower = ret[fold[1] + 1:, :][::-1]
            ret = np.logical_or(upper, lower)
            if fold[0] == "x":
                ret = np.transpose(ret)

            i += 1

        return ret, i
