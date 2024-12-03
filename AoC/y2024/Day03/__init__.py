from typing import Callable, AnyStr, Optional, List, Tuple

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

_DAY = 3


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    return "".join([x for x in data if len(x) > 0])


@Task(year=2024, day=_DAY, task=1)
def task01(data: str, log: Callable[[AnyStr], None]):
    log(f"Input has a length of {len(data)}")
    import re
    data = data.replace(" ", "")
    correct_patterns = re.findall(r"mul\(\d{1,3},\d{1,3}\)", data)
    log(f"There are {len(correct_patterns)} correct multiplication patterns")
    r = 0
    for i, pattern in enumerate(correct_patterns):
        pattern = pattern.split("(")[-1].split(")")[0]
        n1, n2 = pattern.split(",")
        n1, n2 = int(n1), int(n2)
        r += n1 * n2
    return r


@Task(year=2024, day=_DAY, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    log(f"Input has a length of {len(data)}")
    import re
    data = data.replace(" ", "")
    correct_patterns = list(re.finditer(r"mul\(\d{1,3},\d{1,3}\)", data))
    dos = list(re.finditer(r"do\(\)", data))
    donts = list(re.finditer(r"don\'t\(\)", data))
    log(f"There are {len(correct_patterns)} correct multiplication patterns, {len(dos)} dos and {len(donts)} don'ts")
    thingies = sorted((x for x in correct_patterns + dos + donts), key=lambda x: x.start())
    mul_enabled = True
    r = 0
    c = [0, 0, 0]
    for i, pattern in enumerate(thingies):
        pattern_str = pattern[0]
        if pattern_str == "do()":
            mul_enabled = True
            c[0] += 1
        elif pattern_str == "don't()":
            mul_enabled = False
            c[1] += 1
        elif pattern_str.startswith("mul("):
            c[2] += 1
            if mul_enabled:
                pattern_str = pattern_str.split("(")[-1].split(")")[0]
                n1, n2 = pattern_str.split(",")
                n1, n2 = int(n1), int(n2)
                r += n1 * n2
        else:
            raise Exception(pattern)
    log(str(c))
    return r
