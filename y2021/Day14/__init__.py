import time
from typing import Any, Optional, List, Tuple, Dict

from AoC_Companion.Day import Day, TaskResult, StarTask


class Day14(Day):

    def __init__(self, year: int, sim_steps: Optional[Dict[str, int]] = None):
        super().__init__(year)
        self._sim_steps: Dict[int, int] = {} if sim_steps is None else {int(k): v for k, v in sim_steps.items()}

    def pre_process_input(self, data: Any) -> Any:
        data: List[str] = super().pre_process_input(data=data)
        start = data[0].strip()
        rules: Dict[Tuple[str, str], str] = {}
        for line in (d for d in data[1:] if len(d) > 0):
            line1, line2 = line.split("->")
            rules[tuple(line1.strip())] = line2.strip()
        return start, rules

    def run_t1(self, data: Tuple[str, Dict[Tuple[str, str], str]]) -> Optional[TaskResult]:
        pass

    def run_t2(self, data: Tuple[str, Dict[Tuple[str, str], str]]) -> Optional[TaskResult]:
        pass

    def run(self, task: StarTask, data: Any) -> Optional[TaskResult]:
        t1 = time.time()
        steps = self._sim_steps.get(task.value, 1)
        counts = self.do_polymer(start=data[0], rules=data[1], steps=steps)
        ret = max(counts.values()) - min(counts.values())
        log = [
            f"Simulated polymer creation for {steps} steps",
            f"In the end {len(counts)} elements are involved",
            f"Length of final polymer is {sum(counts.values())}"
        ]
        t2 = time.time()
        return TaskResult(ret, duration=t2 - t1, day=self, task=task, log=log)

    @staticmethod
    def do_polymer(start: str, rules: Dict[Tuple[str, str], str], steps: int) -> Dict[str, int]:
        combs: Dict[Tuple[str, str], int] = {}

        def inc_comb(_combs: Dict[Tuple[str, str], int], _comb: Tuple[str, str], _amount: int = 1):
            if _comb not in _combs:
                _combs[_comb] = 0
            _combs[_comb] += _amount

        for j in range(len(start) - 1):
            inc_comb(_combs=combs, _comb=(start[j], start[j + 1]))

        for i in range(steps):
            new_combs = {}
            for comb, amount in combs.items():
                if comb in rules:
                    inc_comb(_combs=new_combs, _comb=(comb[0], rules[comb]), _amount=amount)
                    inc_comb(_combs=new_combs, _comb=(rules[comb], comb[1]), _amount=amount)
            combs = new_combs

        counts: Dict[str, int] = {}

        for comb, amount in combs.items():
            if comb[0] not in counts:
                counts[comb[0]] = 0
            counts[comb[0]] += amount

        counts[start[-1]] += 1

        return counts
