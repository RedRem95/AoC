from typing import Callable, AnyStr, List, Any

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2021, day=3)
def pre_process_input(data: Any) -> Any:
    data = [[int(y) for y in x] for x in data if len(x) > 0]
    return np.array(data, dtype=np.int32)


@Task(year=2021, day=3, task=1)
def run_t1(data: Any, log) -> Any:
    gamma = find_most_common(data=data)
    eps = find_least_common(data=data)
    log("\n".join([
        f"Log has {data.shape[0]} lines. Every line has {data.shape[1]} values",
        f"Extraction from log:",
        f"  Gamma: {''.join(str(x) for x in gamma)}",
        f"  Eps  : {''.join(str(x) for x in eps)}"
    ]))
    gamma = bin_to_int(data=gamma)
    eps = bin_to_int(data=eps)
    power = gamma * eps
    log("\n".join([
        f"Converted to decimal:",
        f"  Gamma: {gamma}",
        f"  Eps  : {eps}",
        f"Resulting calculation:",
        f"  Power: {gamma * eps=}"
    ]))
    return power


@Task(year=2021, day=3, task=2)
def run_t2(data: Any, log) -> Any:
    data: np.ndarray
    oxygen = data.copy()
    for i in range(data.shape[1]):
        common = find_most_common(data=oxygen)
        oxygen = oxygen[oxygen[:, i] == common[i], :]
        if oxygen.shape[0] == 1:
            break
    co2 = data.copy()
    for i in range(data.shape[1]):
        common = find_least_common(data=co2)
        co2 = co2[co2[:, i] == common[i], :]
        if co2.shape[0] == 1:
            break
    oxygen = oxygen[0]
    co2 = co2[0]
    log("\n".join([
        f"Log has {data.shape[0]} lines. Every line has {data.shape[1]} values",
        f"Extraction from log:",
        f"  Oxygen      : {''.join(str(x) for x in oxygen)}",
        f"  CO2         : {''.join(str(x) for x in co2)}"
    ]))
    oxygen = bin_to_int(data=oxygen)
    co2 = bin_to_int(data=co2)
    life_support = oxygen * co2
    log("\n".join([
        f"Converted to decimal:",
        f"  Oxygen      : {oxygen}",
        f"  CO2         : {co2}",
        f"Resulting calculation:",
        f"  Life Support: {oxygen * co2=}"
    ]))
    return life_support


def find_most_common(data: np.ndarray) -> np.ndarray:
    return (np.mean(data, axis=0) + 0.5).astype(int)


def find_least_common(data: np.ndarray) -> np.ndarray:
    common = find_most_common(data=data)
    ret = np.zeros_like(common)
    ret[common == 0] = 1
    return ret


def bin_to_int(data: np.ndarray) -> int:
    return int("".join([str(x) for x in data]), 2)
