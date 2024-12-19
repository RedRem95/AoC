import os.path
from functools import lru_cache
from typing import Callable, AnyStr, Tuple, List, Iterable

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor
from tqdm import tqdm

if os.path.basename(os.path.dirname(os.path.dirname(__file__))).startswith("y"):
    _YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[len("y"):])
else:
    raise Exception()

if os.path.basename(os.path.dirname(__file__)).startswith("Day"):
    _DAY = int(os.path.basename(os.path.dirname(__file__))[len("Day"):])
else:
    raise Exception()


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    towels = []
    designs = []
    for line in (x for x in data if len(x) > 0):
        if len(towels) <= 1:
            towels.extend([x.strip() for x in line.split(",")])
        else:
            designs.append(line.strip())
    return towels, designs


def design_possible(towels: Iterable[str]):
    @lru_cache(maxsize=None)
    def fun(design: str):
        if len(design) <= 0:
            return 1
        ret = 0
        for towel in towels:
            if design.startswith(towel):
                ret += fun(design[len(towel):])
        return ret

    return fun


def check_designs(designs: List[str], towels: Iterable[str], pb: bool = False):
    if pb:
        designs = tqdm(designs, desc="Checking designs", leave=False, unit="designs")
    compare_fun = design_possible(towels=towels)
    ret = []
    for design in designs:
        ret.append(compare_fun(design))
    return ret


@Task(year=2024, day=_DAY, task=1)
def task01(data, log: Callable[[AnyStr], None]):
    towels, designs = data
    log(f"Checking how many of the {len(designs)} are creatable using the unique {len(towels)} towels")
    towel_combinations = check_designs(designs=designs, towels=towels)
    ret = sum(1 if x > 0 else 0 for x in towel_combinations)
    log(f"{ret}/{len(designs)} are doable. That are {ret / len(designs) * 100:.2f}%")
    return ret


@Task(year=2024, day=_DAY, task=2)
def task02(data: List[Tuple[int, int]], log: Callable[[AnyStr], None]):
    towels, designs = data
    log(f"Checking how in how many ways the {len(designs)} designs can be created using {len(towels)} unique towels")
    towel_combinations = check_designs(designs=designs, towels=towels)
    ret = sum(towel_combinations)
    log(f"There are {ret} unique combinations. Have fun")
    return ret
