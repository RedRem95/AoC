from typing import Callable, AnyStr, List, Any, Optional, Dict, Tuple, Iterable, Set, Union, Iterator
import os
import json
import enum
import queue
import itertools
from queue import LifoQueue
from itertools import permutations
from functools import lru_cache
from collections import Counter

import numpy as np
from scipy.spatial import distance
from scipy.signal import convolve2d
import matplotlib
import matplotlib.pyplot as plt

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

from .alu import ALU
from .monad import MONAD


@Preprocessor(year=2021, day=24)
def pre_process_input(data: Any) -> Any:
    data = [x for x in data if len(x) > 0]
    ret = data
    return ret


# @Task(year=2021, day=24, task=1)
def run_t1(data: List[str], log: Callable[[str], None]) -> Any:
    monad = MONAD(instruction_lines=data)
    valid_numbers = monad.find_valid_numbers()
    # biggest_num = monad.force_biggest_number()
    return valid_numbers[0], valid_numbers[-1]


# @Task(year=2021, day=24, task=2)
def run_t2(data: Any, log: Callable[[str], None]) -> Any:
    return None
