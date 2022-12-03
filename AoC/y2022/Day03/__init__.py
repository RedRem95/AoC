from typing import Callable, AnyStr, List, Tuple, Optional

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022, day=3)
def preproc_1(data):
    ret = []
    for line in data:
        line = line.strip()
        if len(line) <= 0:
            continue
        half_point = len(line) / 2
        if int(half_point) != half_point:
            raise Exception()
        half_point = int(half_point)
        ret.append((line[:half_point], line[half_point:]))
    return ret


def _value(c: str) -> int:
    if len(c) != 1:
        return sum(_value(_c) for _c in c)
    if c.isupper():
        return 27 + ord(c) - ord("A")
    if c.islower():
        return 1 + ord(c) - ord("a")
    raise Exception()


@Task(year=2022, day=3, task=1)
def task01(data: List[Tuple[str, str]], log: Callable[[AnyStr], None]):
    log(f"There are {len(data)} backpacks with {sum(len(x1) + len(x2) for x1, x2 in data)} items overall")
    s = 0
    for c1, c2 in data:
        c1 = set(c1)
        c2 = set(c2)
        both = c1.intersection(c2)
        s += _value(c="".join(both))
    log(f"The sum of all misplaced item values is {s}")
    return s


@Task(year=2022, day=3, task=2, extra_config={"group_size": 3})
def task02(data, log: Callable[[AnyStr], None], group_size):
    if len(data) % group_size != 0:
        raise Exception()
    log(f"There are {len(data)} backpacks divided in groups of {group_size}, so {len(data) // group_size} groups")
    s = 0
    group: List[Optional[set]] = [None for _ in range(group_size)]
    for i, (c1, c2) in enumerate(data):
        c1 = set(c1)
        c2 = set(c2)
        group[i % group_size] = c1.union(c2)
        if i % group_size == group_size - 1:
            common_group = set.intersection(*group)
            s += _value("".join(common_group))
    log(f"The sum of all group badges values is {s}")
    return s
