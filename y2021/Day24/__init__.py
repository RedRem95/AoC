import itertools
from collections import Counter
from typing import Any, Optional, List, Tuple, Callable, Set, Union, Iterable
import queue

import numpy as np
from AoC_Companion.Day import Day, TaskResult

from .alu import ALU
from .monad import MONAD


class Day24(Day):

    def __init__(self, year: int):
        super().__init__(year)

    def pre_process_input(self, data: Any) -> Any:
        data: List[str] = super().pre_process_input(data=data)
        data = [x for x in data if len(x) > 0]
        ret = data
        return ret

    def run_t1(self, data: List[str]) -> Optional[TaskResult]:
        monad = MONAD(instruction_lines=data)
        valid_numbers = monad.find_valid_numbers()
        # biggest_num = monad.force_biggest_number()
        return TaskResult((valid_numbers[0], valid_numbers[-1]))

    def run_t2(self, data: Any) -> Optional[TaskResult]:
        return TaskResult(None)
