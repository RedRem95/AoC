import os.path
from typing import Callable, AnyStr, List

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor

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
    element = []
    keys, locks = [], []

    def process_element():
        if len(element) == 0:
            return
        is_key = all(x == "#" for x in element[-1])
        is_lock = all(x == "#" for x in element[0])
        if is_key and is_lock:
            raise Exception("Cant be key and lock")
        if not (is_key or is_lock):
            raise Exception("Has to be key or lock")
        if is_key:
            keys.append([])
            for i in range(max(len(x) for x in element)):
                j = 0
                while j < len(element) and element[-j - 1][i] == "#":
                    j += 1
                keys[-1].append(j - 1)
        if is_lock:
            locks.append([])
            for i in range(max(len(x) for x in element)):
                j = 0
                while j < len(element) and element[j][i] == "#":
                    j += 1
                locks[-1].append(j - 1)
        element.clear()

    for line in data:
        if len(line) == 0:
            process_element()
        else:
            element.append(line)
    process_element()
    return keys, locks


def key_lock_fit(key: List[int], lock: List[int]) -> bool:
    if len(key) != len(lock):
        return False
    return all(x + y <= 5 for x, y in zip(key, lock))


@Task(year=2024, day=_DAY, task=1)
def task01(data, log: Callable[[AnyStr], None]):
    from tqdm import tqdm
    keys, locks = data
    ret = 0
    with tqdm(total=len(keys) * len(locks), desc="Testing combinations", leave=False) as pbar:
        for key in keys:
            for lock in locks:
                if key_lock_fit(key=key, lock=lock):
                    ret += 1
                pbar.update(1)

    return ret


@Task(year=2024, day=_DAY, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    return None
