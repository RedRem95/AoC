import os.path
from collections import defaultdict
from itertools import combinations
from typing import Callable, AnyStr, Dict, Set, Tuple

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


def _and(x, y):
    return x & y


def _or(x, y):
    return x or y


def _xor(x, y):
    return x ^ y


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    ret = defaultdict(set)
    for line in (x for x in data if len(x) > 0):
        f, t = line.split("-")
        ret[f].add(t)
        ret[t].add(f)
    return ret


def get_subnetworks(net_plan: Dict[str, Set[str]], subnetwork_len: int) -> Set[Tuple[str, ...]]:
    potentials = set(x for x in net_plan.keys() if len(net_plan[x]) >= subnetwork_len - 1)
    networks = set()
    for pot in potentials:
        combs = list(combinations(net_plan[pot], subnetwork_len - 1))
        for comb in combs:
            if all(c == x or c in net_plan[x] for c in comb for x in comb):
                networks.add(tuple(sorted(comb + (pot,))))
    return networks


@Task(year=2024, day=_DAY, task=1)
def task01(data, log: Callable[[AnyStr], None]):
    pc_start = "t"
    subnetwork_size = 3
    log(f"Searching for all subnetworks of size {subnetwork_size} with devices starting with {pc_start}")
    networks = get_subnetworks(net_plan=data, subnetwork_len=subnetwork_size)
    ret = sum(1 if any(y.startswith(pc_start) for y in x) else 0 for x in networks)
    log(f"{len(networks)} subnetworks of size {subnetwork_size} found. "
        f"{ret} of these start with {pc_start}. That is {ret / len(networks) * 100:.2f}%")
    return ret


@Task(year=2024, day=_DAY, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    log(f"Searching for biggest subnetwork in a network of {len(data)} devices")
    for req_len in range(max(len(x) for x in data.values()), 2, -1):
        networks = get_subnetworks(net_plan=data, subnetwork_len=req_len)
        if len(networks) <= 0:
            continue
        else:
            ret = list(networks)[0]
            log(f"LAN-Party is played by {len(ret)} participants: {','.join(ret)}")
            return ",".join(ret)
