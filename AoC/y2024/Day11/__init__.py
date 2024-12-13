import os.path
from typing import Callable, AnyStr, List, Tuple
from functools import lru_cache

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor
from tqdm import trange

if os.path.basename(os.path.dirname(__file__)).startswith("Day"):
    _DAY = int(os.path.basename(os.path.dirname(__file__))[len("Day"):])
else:
    raise Exception()


@lru_cache(maxsize=None)
def splitter(val: int) -> List[int]:
    val_str = str(val)
    return [int(val_str[:len(val_str)//2]), int(val_str[len(val_str)//2:])]


_RULES: List[Tuple[Callable[[int], bool], Callable[[int], List[int]]]] = [
    (lambda x: x == 0, lambda x: [1]),
    (lambda x: len(str(x)) % 2 == 0, splitter),
    (lambda x: True, lambda x: [x * 2024])
]


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    return [int(y) for y in [x for x in data if len(x) > 0][0].split(" ") if len(y) > 0]


@lru_cache(maxsize=None)
def stone_count(stone: int, blinks_to_go: int):
    if blinks_to_go <= 0:
        return 1
    for rc, r in _RULES:
        if rc(stone):
            return sum(stone_count(stone=x, blinks_to_go=blinks_to_go - 1) for x in r(stone))
    else:
        raise Exception()


def run(stones: List[int], log: Callable[[AnyStr], None], blink_count: int):
    log(f"You are going to blink {blink_count} times at {len(stones)} stones")
    ret = sum(stone_count(stone=x, blinks_to_go=blink_count) for x in stones)
    log(f"After you blinked {blink_count} times at the {len(stones)} stones there are {ret} stones")
    return ret


@Task(year=2024, day=_DAY, task=1, extra_config={"blink_count": 25})
def task01(data, log: Callable[[AnyStr], None], blink_count: int):
    return run(stones=data, log=log, blink_count=blink_count)


@Task(year=2024, day=_DAY, task=2, extra_config={"blink_count": 75})
def task02(data, log: Callable[[AnyStr], None], blink_count: int):
    return run(stones=data, log=log, blink_count=blink_count)
