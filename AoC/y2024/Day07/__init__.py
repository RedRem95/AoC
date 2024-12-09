from typing import Callable, AnyStr, List, Union, Iterable

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor

_DAY = 7


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    ret = []
    for line in (x.strip() for x in data if len(x) > 0):
        r, v = line.split(":")
        r = int(r.strip())
        v = [int(x.strip()) for x in v.split(" ") if len(x.strip()) > 0]
        ret.append((r, v))
    return ret


def check_line(result: Union[int, float], values: List[int],
               operators: Iterable[Callable[[int, int], Union[int, float]]]) -> bool:
    if int(result) != result or result < 0 or len(values) <= 0:
        return False
    result = int(result)
    if len(values) == 1:
        return result == values[0]
    for op in operators:
        if check_line(result=op(result, values[-1]), values=values[:-1], operators=operators):
            return True
    return False


def add(v1, v2):
    return v1 - v2


def mult(v1, v2):
    return v1 / v2


def concat(v1, v2):
    v1, v2 = str(v1), str(v2)
    if v1.endswith(v2) and len(v1) > len(v2):
        return int(v1[:-len(v2)])
    return -1


def run(data, log: Callable[[AnyStr], None], operators):
    log(f"Checking {len(data)} lines with equations")
    log(f"Allowed operators: {', '.join(f'{x.__name__}-Operator' for x in operators)}")
    ret_data = [result for result, values in data if check_line(result, values, operators)]
    ret = sum(ret_data)
    log(f"{len(ret_data)} equations can be solved. That are {len(ret_data)/len(data)*100:.2f}% of the equations")
    log(f"Sum of all solvable equations is {ret}")
    return ret


@Task(year=2024, day=_DAY, task=1)
def task01(data, log: Callable[[AnyStr], None]):
    return run(data=data, log=log, operators=[add, mult])


@Task(year=2024, day=_DAY, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    return run(data=data, log=log, operators=[add, mult, concat])
