from typing import Callable, AnyStr, Dict

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

from .monkey import load_monkeys, Monkey, Item, VALUE_TYPE


@Preprocessor(year=2022, day=11)
def preproc_1(data):
    monkey_horde = load_monkeys(lines=data)
    for k in sorted(monkey_horde.keys()):
        # print(k, monkey_horde[k])
        pass
    return monkey_horde


@Task(year=2022, day=11, task=1, extra_config={"rounds": 20})
def task01(monkey_horde: Dict[int, Monkey], log: Callable[[AnyStr], None], rounds: int):
    log("Your worry is divided by 3 cause you good")

    def relief_callback(item: Item) -> Item:
        item.value = item.value // 3
        return item

    ret = _sim(monkey_horde=monkey_horde, log=log, rounds=rounds, callback=relief_callback)
    return np.prod(sorted(ret.values(), reverse=True)[:2])


@Task(year=2022, day=11, task=2, extra_config={"rounds": 10_000})
def task02(monkey_horde: Dict[int, Monkey], log: Callable[[AnyStr], None], rounds: int):

    div = VALUE_TYPE(np.prod([x.condition.value for x in monkey_horde.values()]))
    log(f"To keep values in check the worry is cut by {div} every round")

    def relief_callback(item: Item) -> Item:
        item.value = item.value % div
        return item

    ret = _sim(monkey_horde=monkey_horde, log=log, rounds=rounds, callback=relief_callback)
    return np.prod(sorted(ret.values(), reverse=True)[:2])


def _sim(
        monkey_horde: Dict[int, Monkey], log: Callable[[AnyStr], None], rounds: int, callback: Callable[[Item], Item],
        verbose: bool = False
) -> Dict[int, int]:
    log(f"Simulating for {rounds} rounds and {len(monkey_horde)} monkeys")
    if verbose:
        log(f"Start monkeys:")
        for k in sorted(monkey_horde.keys()):
            log(f"{k:4d}: {monkey_horde[k]}")
    ret: Dict[int, int] = {k: 0 for k in monkey_horde.keys()}
    for i in range(1, rounds + 1):
        for k in sorted(monkey_horde.keys()):
            ret[k] += monkey_horde[k].execute(relief_callback=callback)
    if verbose:
        log(f"Monkeys after {rounds} rounds:")
        for k in sorted(monkey_horde.keys()):
            log(f"{k:4d}: {monkey_horde[k]}, threw items {ret[k]} times")
    log(f"In the end your items got thrown {sum(ret.values())} times")
    return ret
