from typing import Callable, AnyStr, List, Optional

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022, day=13)
def preproc_1(data):
    ret = []
    for i in range(0, len(data), 3):
        line1 = data[i].strip()
        line2 = data[i + 1].strip()
        if len(line1) <= 0 or len(line2) <= 0:
            raise Exception()
        v1 = eval(line1)
        v2 = eval(line2)
        ret.append((v1, v2))
    return ret


@Task(year=2022, day=13, task=1)
def task01(data, log: Callable[[AnyStr], None]):
    ret = []
    log(f"Comparing {len(data)} pairs of data")
    for i in range(len(data)):
        if _compare(list1=data[i][0], list2=data[i][1], log=lambda x: None):
            ret.append(i + 1)
    log(f"{len(ret)} pairs are already sorted. Sum 1 based indices is {sum(ret)}")
    return sum(ret)


@Task(year=2022, day=13, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    divider_packages = [[[2]], [[6]]]
    log(f"Adding divider packets: {', '.join(str(x) for x in divider_packages)}")
    all_packets = divider_packages.copy()
    for p1, p2 in data:
        all_packets.append(p1)
        all_packets.append(p2)

    log(f"Sorting {len(all_packets)} packets")

    sorted_packets = sort(all_packets, compare_key=lambda x, y: _compare(x, y, lambda _: None), in_place=False)
    ret = []
    for i in range(len(sorted_packets)):
        if sorted_packets[i] in divider_packages:
            ret.append(i + 1)
    if len(ret) != len(divider_packages):
        raise Exception()
    log(f"Divider packets are at 1 based indices {', '.join(str(x) for x in ret)}")
    return ret[0] * ret[1]


def _compare(list1: List, list2: List, log: Callable[[AnyStr], None]) -> Optional[bool]:
    log(f"Compare {list1}, {list2}")
    i = 0
    while i < max(len(list1), len(list2)):
        if i >= len(list1):
            if i >= len(list2):
                raise Exception()
            log(f" - 1 shorter")
            return True
        if i >= len(list2):
            log(f" - 2 shorter")
            return False
        item1, item2 = list1[i], list2[i]
        log(f" - Compare {item1}, {item2}")
        if isinstance(item1, int) and isinstance(item2, int):
            if item1 == item2:
                pass
            else:
                log(f" - Result {item1} < {item2} => {item1 < item2}")
                return item1 < item2
        else:
            if isinstance(item1, int):
                log(f" - 1 is single. Convert list")
                item1 = [item1]
            if isinstance(item2, int):
                log(f" - 2 is single. Convert list")
                item2 = [item2]
            _ret = _compare(list1=item1, list2=item2, log=log)
            log(f" - Subcompare: {_ret}")
            if _ret is not None:
                return _ret
        i += 1
    return None


def sort(compare_list: List, compare_key: Callable[[List, List], bool], in_place: bool = False) -> List:
    if not in_place:
        from copy import deepcopy
        compare_list = deepcopy(compare_list)
    for i in range(1, len(compare_list)):
        for j in range(i - 1, -1, -1):
            if not compare_key(compare_list[j], compare_list[j + 1]):
                compare_list[j + 1], compare_list[j] = compare_list[j], compare_list[j + 1]
            else:
                break
    return compare_list
