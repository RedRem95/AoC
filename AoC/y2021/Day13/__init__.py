from typing import Callable, AnyStr, List, Any, Optional, Dict, Tuple, Iterable, Set, Union
import os
import json
import enum
from queue import LifoQueue

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2021, day=13)
def pre_process_input(data: Any) -> Any:
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


@Task(year=2021, day=13, task=1)
def run_t1(data: Tuple[np.ndarray, List[Tuple[str, int]]], log: Callable[[str], None]) -> Any:
    after_fold, folds = _do_folds(data=data[0], folds=data[1], amount=1)
    ret = np.sum(after_fold)
    log(f"After 1 fold {ret} dots are visible")
    return ret


@Task(year=2021, day=13, task=2)
def run_t2(data: Tuple[np.ndarray, List[Tuple[str, int]]], log: Callable[[str], None]) -> Any:
    after_fold, folds = _do_folds(data=data[0], folds=data[1], amount=np.inf)
    ret = [[]]
    for i in range(after_fold.shape[0]):
        for j in range(after_fold.shape[1]):
            if after_fold[i, j] == 1:
                ret[-1].append("#")
            else:
                ret[-1].append(" ")
        ret.append([])
    log(f"After {folds} folds {np.sum(after_fold)} dots are visible")
    log("\n".join(["".join(x for x in y) for y in ret]))
    return "See log"


def _do_folds(data: np.ndarray, folds: List[Tuple[str, int]], amount: Union[int, float]) -> Tuple[np.ndarray, int]:
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
