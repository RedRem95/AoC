import os.path
from typing import Callable, AnyStr, Union, Dict, Any, Tuple, List

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022, day=7)
def preproc_1(data):
    ret = []
    for line in data:
        line = str(line).strip()
        if len(line) <= 0:
            continue
        spec, cont = line.split(" ", 1)
        try:
            spec = int(spec)
        except ValueError:
            pass
        ret.append((spec, cont))
    return ret


@Task(year=2022, day=7, task=1, extra_config={"max_size": 100000})
def task01(data, log: Callable[[AnyStr], None], max_size: int):
    structure = _build_structure(data=data)
    log(f"Build structure from {len(data)} lines of data")
    total_used, dir_sizes = _calc_size(structure=structure)
    log(f"The total space used is {total_used}")

    log(f"Finding all files and folders that are smaller that {max_size}")
    small_files_folgers = [(x, s) for x, s in dir_sizes.items() if s <= max_size]
    ret = sum(x[1] for x in small_files_folgers)
    log(f"Found {len(small_files_folgers)} small files and folders. Together they are {ret} big")

    return ret


@Task(year=2022, day=7, task=2, extra_config={"total": 70000000, "needed": 30000000})
def task02(data, log: Callable[[AnyStr], None], total: int, needed: int):
    structure = _build_structure(data=data)
    log(f"Build structure from {len(data)} lines of data")
    total_used, dir_sizes = _calc_size(structure=structure)
    log(f"The total space used is {total_used}")

    currently_free = total - total_used
    log(f"You have {currently_free}/{total} ({100 * currently_free / total:6.2f}%) free")

    need_to_free = needed - currently_free
    log(f"You need free space of {needed} so you need at least {need_to_free} to be freed")

    if need_to_free <= 0:
        log(f"You already have enough free space. PARTY")
        return None

    candidates = [(x, s) for x, s in dir_sizes.items() if s >= need_to_free]
    log(f"Found {len(candidates)} candidates to be deleted")

    ret_name, ret_size = sorted(candidates, key=lambda x: x[1])[0]
    log(f"The smallest candidate is {ret_name} which is {ret_size} big (so {ret_size - need_to_free} too much :/)")

    return ret_size


def _build_structure(data: List[Tuple[Union[str, int], str]]):
    cur_dir = tuple()
    structure: Dict[str, Any] = {}

    for spec, content in data:
        spec: Union[str, int]
        content: str

        if spec == "$":
            if content.split(" ", 1)[0] == "cd":
                new_dir = content.split(" ", 1)[1]
                if new_dir == "..":
                    cur_dir = cur_dir[:-1]
                else:
                    cur_dir = (*cur_dir, new_dir)
        if isinstance(spec, int):
            trav = structure
            for d in cur_dir:
                if d not in trav:
                    trav[d] = {}
                trav = trav[d]
            trav[content] = spec

    return structure


def _calc_size(structure: Dict[str, Any]) -> Tuple[int, Dict[str, int]]:
    sum_sizes, sub_sizes = 0, {}
    for k, v in structure.items():
        if isinstance(v, dict):
            _x, _y = _calc_size(structure=v)
            sum_sizes += _x
            sub_sizes[k] = _x
            for _k, _v in _y.items():
                _k = f"{k}{'' if k.endswith('/') else '/'}{_k}"
                # _k = os.path.join(k, _k)
                sub_sizes[_k] = _v
        else:
            sum_sizes += v
    return sum_sizes, sub_sizes
