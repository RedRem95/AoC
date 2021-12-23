import itertools
from collections import Counter
from typing import Any, Optional, List, Tuple, Callable, Set, Union, Iterable

import numpy as np
from AoC_Companion.Day import Day, TaskResult


class Day24(Day):

    def __init__(self, year: int):
        super().__init__(year)

    def pre_process_input(self, data: Any) -> Any:
        data: List[str] = super().pre_process_input(data=data)
        data = [x for x in data if len(x) > 0]
        ret = data
        return ret

    def run_t1(self, data: Any) -> Optional[TaskResult]:
        return TaskResult(None)

    def run_t2(self, data: Any) -> Optional[TaskResult]:
        return TaskResult(None)
