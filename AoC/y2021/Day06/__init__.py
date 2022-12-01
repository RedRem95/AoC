from typing import Callable, AnyStr, List, Any, Optional, Dict, Tuple, Iterable
import os
import json

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

_config_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(_config_path, "r", encoding="utf-8") as _f_config:
    _config = json.load(_f_config)


@Preprocessor(year=2021, day=6)
def pre_process_input(data: Any) -> Any:
    ret = [int(x) for x in data[0].split(",")]
    return ret


@Task(year=2021, day=6, task=1, extra_config=_config)
def run_1(data, log, days: Dict[str, int], graphs: bool):
    return run(task=1, data=data, log=log, days=days, graphs=graphs)


@Task(year=2021, day=6, task=2, extra_config=_config)
def run_2(data, log, days: Dict[str, int], graphs: bool):
    return run(task=2, data=data, log=log, days=days, graphs=graphs)


def run(task: int, data: Any, log: Callable[[AnyStr], None], days: Dict[str, int], graphs: bool) -> Any:
    days = days.get(str(task), 1)
    log(f"Simulation will run for {days} days")
    log(f"Starting population: {sum(data)}")
    simulated_pops = _sim(init_ages=data, days=days, ret_all=graphs)
    final_population = np.sum(simulated_pops[-1])
    log(f"Final population: {final_population}")
    if graphs:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 1)
        fig: plt.Figure
        ax: plt.Axes
        fig.suptitle("Simulated Population")
        ax.set_title(f"{task} for {days} days")
        ax.plot(simulated_pops.sum(axis=1))
        target_path = os.path.join(os.path.dirname(__file__), f"pop_{task}.png")
        fig.savefig(target_path)
        log(f"Saved plot to {target_path}")
    return final_population


def _sim(init_ages: List[int], days: int, ret_all: bool = False) -> np.ndarray:
    ages = np.zeros((9,), dtype=int)
    for a in init_ages:
        ages[a] += 1
    ret: np.ndarray = np.zeros((days if ret_all else 1, ages.shape[0]), dtype=int)
    for i in range(days):
        parents = ages[0]
        ages[:-1] = ages[1:]
        ages[6] += parents
        ages[8] = parents
        ret[i if ret_all else 0] = ages
    return ret


def _sim_v2(init_ages: List[int], days: int, ret_all: bool = False) -> np.ndarray:
    """
    Different implementation with rotating index.
    Be careful since the indices in resulting array do not correspond with days until the fish create new fish.
    You have to create the rotating index like days % 6 to get the amount of fish that will create new ones next.
    The last two indices are alternating the young ones with the higher wait time until they will create some
    themselves

    :param init_ages:
    :param days:
    :param ret_all:
    :return:
    """
    ages = np.zeros((9,), dtype=int)
    for a in init_ages:
        ages[a] += 1
    ret: np.ndarray = np.zeros((days if ret_all else 1, ages.shape[0]), dtype=int)
    for i in range(days):
        j = i % 6
        m = 7 + (i % 2)
        ages[j], ages[m] = ages[j] + ages[m], ages[j]
        ret[i if ret_all else 0] = ages
    return ret
