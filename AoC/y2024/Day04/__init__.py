from typing import Callable, AnyStr, Optional, List, Tuple

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

_DAY = 4


def _get_lines(orig: Tuple[int, int], bounds: Tuple[Tuple[int, int], Tuple[int, int]], length: int) -> List[
    List[Tuple[int, int]]]:
    r, c = orig
    (minr, minc), (maxr, maxc) = bounds
    ret: List[List[Tuple[int, int]]] = [[] for _ in range(8)]
    for i in range(length):
        ret[0].append((r - i, c + 0))
        ret[1].append((r - i, c + i))
        ret[2].append((r + 0, c + i))
        ret[3].append((r + i, c + i))
        ret[4].append((r + i, c + 0))
        ret[5].append((r + i, c - i))
        ret[6].append((r + 0, c - i))
        ret[7].append((r - i, c - i))
    return [x if all(minr <= r <= maxr and minc <= c <= maxc for r, c in x) else None for x in ret]


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    return [list(x) for x in data if len(x) > 0]


@Task(year=2024, day=_DAY, task=1)
def task01(data: str, log: Callable[[AnyStr], None]):
    find_word = "XMAS"
    ret = 0
    if not all(len(x) == len(data[0]) for x in data):
        raise Exception()
    bounds = ((0, 0), (len(data) - 1, len(data[0]) - 1))
    log(f"Searching for {find_word}")
    log(f"Grid has a size of {bounds[1][1]}x{bounds[1][0]}")
    for r in range(len(data)):
        for c in range(len(data[r])):
            if data[r][c] == find_word[0]:
                # log(str((r, c)))
                lines = _get_lines((r, c), bounds, len(find_word))
                # log(str(lines))
                for line in (x for x in lines if x is not None):
                    for i, (cr, cc) in enumerate(line):
                        if not data[cr][cc] == find_word[i]:
                            break
                    else:
                        ret += 1
    log(f"Found {ret} occurrences of {find_word}")
    return ret


@Task(year=2024, day=_DAY, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    find_word = "MAS"
    if len(find_word) % 2 == 0:
        raise Exception("The word you can search for has to be of uneven length.")
    if find_word == find_word[::-1]:
        raise Exception("The word you are searching for has to be not the same reading front to back to back to front.")
    if not all(len(x) == len(data[0]) for x in data):
        raise Exception()
    ret = 0
    bounds = ((0, 0), (len(data) - 1, len(data[0]) - 1))
    log(f"Searching for {find_word} in an X-shape")
    log(f"Grid has a size of {bounds[1][1]}x{bounds[1][0]}")
    for r in range(len(data)):
        for c in range(len(data[r])):
            if data[r][c] == find_word[len(find_word) // 2]:
                lines = _get_lines((r, c), bounds, (len(find_word) // 2) + 1)
                try:
                    diags = [lines[7][::-1] + lines[3][1:], lines[1][::-1] + lines[5][1:]]
                    diags.extend([x[::-1] for x in diags])
                    if sum(all(find_word[i] == data[cr][cc] for i, (cr, cc) in enumerate(d)) for d in diags) == 2:
                        ret += 1
                except TypeError:
                    pass
    log(f"Found {ret} X-shaped occurrences of {find_word}")
    return ret
