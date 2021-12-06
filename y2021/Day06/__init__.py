import os.path
import time
from typing import Any, Optional, List, Dict

import matplotlib.pyplot as plt
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
        final_population = sum(simulated_pops[-1].values())
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
            ax.plot(list(range(len(simulated_pops))), [sum(x.values()) for x in simulated_pops])
            fig.savefig(os.path.join(os.path.dirname(__file__), f"pop_{task.value}.png"))
        return TaskResult(final_population, day=self, task=task, duration=t2 - t1, log=log)

    def run_t1(self, data: List[int], days: int = None) -> Optional[TaskResult]:
        pass

    def run_t2(self, data: Any) -> Optional[TaskResult]:
        pass

    @staticmethod
    def _sim(init_ages: List[int], days: int, ret_all: bool = False) -> List[Dict[int, int]]:
        z_m: Dict[int, int] = {x: 0 for x in range(9)}
        m: List[Dict[int, int], Dict[int, int]] = [z_m.copy(), {}]
        for d in init_ages:
            m[0][d] += 1
        ret: List[Dict[int, int]] = [m[0].copy()]
        for i in range(days):
            m[(i + 1) % 2] = z_m.copy()
            for k, v in m[i % 2].items():
                if k == 0:
                    m[(i + 1) % 2][6] += v
                    m[(i + 1) % 2][8] += v
                else:
                    m[(i + 1) % 2][k - 1] += v
            if ret_all:
                ret.append(m[(i + 1) % 2].copy())
            else:
                ret[0] = m[(i + 1) % 2].copy()
        return ret
