from typing import Callable, AnyStr, Dict, Tuple, List

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022, day=16)
def preproc_1(data):
    ret = {}
    for line in data:
        line = line.strip()
        if len(line) <= 0:
            continue
        valve, tunnels = line.split(";")
        valve_id = valve.strip().split(" ")[1]
        valve_flow = int(valve.strip().split("=")[-1])
        tunnel_targets = [x.strip().split(" ")[-1] for x in tunnels.strip().split(",")]
        ret[valve_id] = (valve_flow, tunnel_targets)
    return ret


@Task(year=2022, day=16, task=1)
def task01(data, log: Callable[[AnyStr], None]):
    # best_flow, strategy = _search2(system=data, start_tine=30, start="AA")
    best_flow = _search(system=data, time_remain=30, current="AA", open_valves={})
    return best_flow


@Task(year=2022, day=16, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    # create the result for day 1 task 2
    return 2


def _search2(system: Dict[str, Tuple[int, List[str]]], start_tine: int, start: str) -> Tuple[int, List[str]]:
    current_strategies: List[Tuple[int, str, int, List[str]]] = [(0, start, start_tine, [])]
    while any(x[2] > 0 for x in current_strategies):
        current_strategies.sort(key=lambda x: (len(x[3]), x[0], -x[2]))
        current_flow, current, time_remain, open_strategy = current_strategies.pop()
        if time_remain <= 0:
            return current_flow, open_strategy
            pass
        current_valve, next_options = system[current]
        if current not in open_strategy:
            current_strategies.append(
                (current_flow + (time_remain - 1) * current_valve, current, time_remain - 1, open_strategy + [current])
            )
        for n in next_options:
            current_strategies.append(
                (current_flow, n, time_remain - 1, open_strategy)
            )
    current_strategies.sort(key=lambda x: x[0])
    best = current_strategies[-1]
    return best[0], best[-1]


def _search(
        system: Dict[str, Tuple[int, List[str]]], time_remain: int, current: str, open_valves: Dict[str, int]
) -> Tuple[int, Dict[str, int]]:
    if time_remain <= 0:
        return _sum_flow(system=system, strategy=open_valves), open_valves

    best_flow, best_strategy = 0, {}

    # open_valve
    if current not in open_valves and system[current][0] > 0:
        _open_valves = open_valves.copy()
        _open_valves[current] = time_remain - 1
        _flow, _strategy = _search(system=system, time_remain=time_remain - 1, current=current,
                                   open_valves=_open_valves)
        if _flow > best_flow:
            best_flow = _flow
            best_strategy = best_flow

    for n in system[current][1]:
        _flow, _strategy = _search(system=system, time_remain=time_remain - 1, current=n, open_valves=open_valves)
        if best_strategy > best_flow:
            best_flow = _flow
            best_strategy = best_flow

    return best_flow, best_strategy


def _sum_flow(system: Dict[str, Tuple[int, List[str]]], strategy: Dict[str, int]) -> int:
    return sum(system[k][0] * v for k, v in strategy.items())
