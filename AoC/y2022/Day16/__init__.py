import itertools
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


@Task(year=2022, day=16, task=1, extra_config={"actors": [("AA", 30)]})
def task01(data, log: Callable[[AnyStr], None], actors: List[Tuple[str, int]]):
    best_flow, best_strategy = _find_flow(system=data, log=log, actors=actors)
    return best_flow


@Task(year=2022, day=16, task=2, extra_config={"actors": [("AA", 26), ("AA", 26)]})
def task02(data, log: Callable[[AnyStr], None], actors: List[Tuple[str, int]]):
    best_flow, best_strategy = _find_flow(system=data, log=log, actors=actors)
    return best_flow


def _find_flow(
        system: Dict[str, Tuple[int, List[str]]], actors: List[Tuple[str, int]], log: Callable[[str], None]
) -> Tuple[int, Dict[str, int]]:
    log(f"There are {len(actors)} actors going to close valves")
    for i, (a, t) in enumerate(actors):
        log(f"{i:4d}: Starting at {a:2s} having {t}s")
    paths = _interesting_paths(system=system)
    log(f"There are {len(system)} valves")
    log(f"There are {sum(len(x) for x in paths.values())} interesting paths to use to get to open valves")
    best_flow, best_strategy = _search(
        system=system,
        actors=actors,
        open_valves={},
        paths=paths,
    )
    log(f"You can achieve the best flow of {best_flow} by closing")
    for v, t in sorted(best_strategy.items(), key=lambda x: x[1], reverse=True):
        log(f"Closing {v:2s} at {t:2d} => {system[v][0] * t:d}")
    return best_flow, best_strategy


def _interesting_paths(system: Dict[str, Tuple[int, List[str]]]) -> Dict[str, Dict[str, int]]:
    ret = {}
    for start in system.keys():
        paths = _find_paths(system=system, start=start)
        ret[start] = {k: v for k, v in paths.items() if system[k][0] > 0}
    return ret


def _find_paths(system: Dict[str, Tuple[int, List[str]]], start: str) -> Dict[str, int]:
    ret = {}
    next_neighbors = [(x, 1) for x in system[start][1]]
    while len(next_neighbors) > 0:
        current, dist = next_neighbors.pop(0)
        if current in ret:
            continue
        ret[current] = dist
        next_neighbors.extend([(x, dist + 1) for x in system[current][1]])
    return ret


def _search(
        system: Dict[str, Tuple[int, List[str]]],
        actors: List[Tuple[str, int]],
        open_valves: Dict[str, int],
        paths: Dict[str, Dict[str, int]],
) -> Tuple[int, Dict[str, int]]:
    if all(current[1] <= 0 for current in actors) or all(current[0] in open_valves for current in actors):
        return _sum_flow(system=system, strategy=open_valves), open_valves

    for i in range(len(actors)):
        current, time_remain = actors[i]
        if time_remain > 0 and system[current][0] > 0 and current not in open_valves:
            actors[i] = (current, time_remain - 1)
            open_valves[current] = time_remain - 1
    best_flow = _sum_flow(system=system, strategy=open_valves)
    best_strategy = open_valves

    combinations = (x for x in itertools.product(*[paths[x].keys() for x in (y[0] for y in actors)]) if
                    len(x) == 1 or len(set(x)) == len(actors))
    combinations = (x for x in combinations if not any(_n in open_valves for _n in x))
    # print(len(combinations))

    for n in combinations:
        next_actors = [
            (_n, time_remain - paths[current][_n]) for (current, time_remain), _n in zip(actors, n)
        ]
        _flow, _strategy = _search(
            system=system,
            actors=next_actors,
            open_valves=open_valves.copy(),
            paths=paths
        )
        if _flow > best_flow:
            best_flow = _flow
            best_strategy = _strategy

    return best_flow, best_strategy


def _create_combinations(base: List[str], n: int) -> List[List[str]]:
    if n <= 0:
        return []
    ret = []
    for i in range(len(base)):
        curr_base = base.copy()
        current = curr_base.pop(i)
        ret.extend([current] + x for x in _create_combinations(base=curr_base, n=n - 1))
    return ret


def _sum_flow(system: Dict[str, Tuple[int, List[str]]], strategy: Dict[str, int]) -> int:
    return sum(system[k][0] * v for k, v in strategy.items())
