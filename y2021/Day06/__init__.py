import os.path
import time
from typing import Any, Optional, List, Dict

import matplotlib.pyplot as plt
import numpy as np
from AoC_Companion.Day import Day, TaskResult, StarTask


class Day06(Day):

    def __init__(self, year: int, days: Optional[Dict[str, int]] = None, graphs: Optional[bool] = True):
        super().__init__(year)
        self._days: Dict[int, int] = {} if days is None else {int(k): v for k, v in days.items()}
        self._graphs = True if graphs is None else bool(graphs)

    def pre_process_input(self, data: Any) -> Any:
        data: List[str] = super().pre_process_input(data=data)
        ret = [int(x) for x in data[0].split(",")]
        return ret

    def run(self, task: StarTask, data: Any) -> Optional[TaskResult]:
        t1 = time.time()
        days = self._days.get(task.value, 1)
        log = [
            f"Simulation will run for {days} days",
            f"Starting population: {sum(data)}"
        ]
        simulated_pops = self._sim(init_ages=data, days=days, ret_all=self._graphs)
        final_population = np.sum(simulated_pops[-1])
        log.append(
            f"Final population: {final_population}"
        )
        t2 = time.time()
        if self._graphs:
            fig, ax = plt.subplots(1, 1)
            fig: plt.Figure
            ax: plt.Axes
            fig.suptitle("Simulated Population")
            ax.set_title(f"{task.name} for {days} days")
            ax.plot(simulated_pops.sum(axis=1))
            fig.savefig(os.path.join(os.path.dirname(__file__), f"pop_{task.value}.png"))
        return TaskResult(final_population, day=self, task=task, duration=t2 - t1, log=log)

    def run_t1(self, data: List[int], days: int = None) -> Optional[TaskResult]:
        pass

    def run_t2(self, data: Any) -> Optional[TaskResult]:
        pass

    @staticmethod
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

    @staticmethod
    def _sim_v2(init_ages: List[int], days: int, ret_all: bool = False) -> np.ndarray:
        """
        Different implementation with rotating index.
        Be careful since the indices in resulting array do not correspond with days until the fish create new fish.
        You have to create the rotating index like days % 6 to get the amount of fish that will create new ones next.
        The last two indices are alternating the young ones with the higher wait time until they will create some
        themself

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
