from typing import Callable, AnyStr, Optional, List, Tuple, Dict, Set
from collections import defaultdict

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

_DAY = 5


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    in_updates = False
    rules = defaultdict(set)
    updates = []
    for line in data:
        if len(line) <= 0:
            if in_updates:
                break
            in_updates = True
        elif in_updates:
            updates.append([int(x) for x in line.split(",")])
        else:
            p1, p2 = line.split('|')
            rules[int(p1)].add(int(p2))
    return rules, updates


def update_correct(update: List[int], rules: Dict[int, Set[int]]) -> Optional[Tuple[int, int]]:
    for i in range(len(update)):
        for j in range(i+1, len(update)):
            if update[i] in rules[update[j]]:
                return i, j
    return None


@Task(year=2024, day=_DAY, task=1)
def task01(data, log: Callable[[AnyStr], None]):
    rules, updates = data
    log(f"There are {len(rules)} rules for printing to follow and {len(updates)} updates")
    correct_updates = [x for x in updates if update_correct(x, rules) is None]
    log(f"{len(correct_updates)}/{len(updates)} updates were correct. "
        f"That are {len(correct_updates)/len(updates) * 100:.2f}%")
    ret = sum(x[len(x)//2] for x in correct_updates)
    log(f"The middle pages of all correct updates in sum result in {ret}")
    return ret


@Task(year=2024, day=_DAY, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    rules, updates = data
    log(f"There are {len(rules)} rules for printing to follow and {len(updates)} updates")
    fixed_updates = []
    swaps = []
    for update in updates:
        update = [x for x in update]
        update_check = update_correct(update, rules)
        if update_check is None:
            continue
        update_swaps = 0
        while update_check is not None:
            i, j = update_check
            update[i], update[j] = update[j], update[i]
            update_check = update_correct(update, rules)
            update_swaps += 1
        swaps.append(update_swaps)
        fixed_updates.append(update)
    log(f"{len(fixed_updates)}/{len(updates)} updates needed fixing. "
        f"That are {len(fixed_updates)/len(updates) * 100:.2f}%")
    log(f"Performed overall {sum(swaps)} swaps to fix all updates. "
        f"That are {sum(swaps)/len(fixed_updates)} swaps per fix")
    log(f"The maximum number of swaps was {max(swaps)}. On the other hand, the minimum swaps were {min(swaps)}.")
    ret = sum(x[len(x)//2] for x in fixed_updates)
    log(f"The middle pages of all fixed updates in sum result in {ret}")
    return ret
