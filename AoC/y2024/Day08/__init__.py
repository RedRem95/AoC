from collections import defaultdict
from typing import Callable, AnyStr, List, Tuple, Dict, Set, Iterable

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor


def tpl_add(t1: Tuple[int, ...], t2: Tuple[int, ...]) -> Tuple[int, ...]:
    return tuple(i + j for i, j in zip(t1, t2))


_DAY = 8


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    ret = defaultdict(list)
    bounds = [0, 0]
    for line_num, line in enumerate(x.strip() for x in data if len(x) > 0):
        for column_num, ch in enumerate(line):
            if ch == ".":
                pass
            else:
                ret[ch].append((line_num, column_num))
            bounds[1] = max(column_num, bounds[1])
        bounds[0] = max(line_num, bounds[0])
    return ret, tuple(bounds)


def get_antinodes(senders: List[Tuple[int, int]], bounds: Tuple[int, int], max_antinodes: int) -> Set[Tuple[int, int]]:
    ret: Set[Tuple[int, int]] = set()
    for i in range(len(senders)):
        for j in (x for x in range(len(senders)) if x != i):
            p1 = senders[i]
            p2 = senders[j]
            diff = p1[0] - p2[0], p1[1] - p2[1]
            node = p1
            for _ in range(max_antinodes):
                # noinspection PyTypeChecker
                node: Tuple[int, int] = tpl_add(node, diff)
                if not all(0 <= x <= bounds[i] for i, x in enumerate(node)):
                    break
                ret.add(node)

    return ret


def run(mapping: Dict[str, List[Tuple[int, int]]], bounds: Tuple[int, int], log: Callable[[AnyStr], None],
        max_antinodes: int, bonus_antinodes: Iterable[List[Tuple[int, int]]] = None) -> None:
    log(f"There are {len(mapping)} different {sum(len(x) for x in mapping.values())} total antennas")
    log(f"The grid has a size of {bounds[1]}x{bounds[0]}")
    ret = set().union(*[get_antinodes(x, bounds, max_antinodes=max_antinodes) for x in mapping.values()])
    if bonus_antinodes is not None:
        ret = ret.union(*bonus_antinodes)
    log(f"The antennas create {len(ret)} antinodes. That is {len(ret) / (bounds[1] * bounds[0]) * 100:.2f}% of the area")
    return len(ret)


@Task(year=2024, day=_DAY, task=1)
def task01(data: Tuple[Dict[str, List[Tuple[int, int]]], Tuple[int, int]], log: Callable[[AnyStr], None]):
    return run(mapping=data[0], bounds=data[1], log=log, bonus_antinodes=None, max_antinodes=1)


@Task(year=2024, day=_DAY, task=2)
def task02(data: Tuple[Dict[str, List[Tuple[int, int]]], Tuple[int, int]], log: Callable[[AnyStr], None]):
    mapping, bounds = data
    return run(mapping=mapping, bounds=bounds, log=log, bonus_antinodes=mapping.values(), max_antinodes=max(bounds))
