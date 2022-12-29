import heapq
import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, AnyStr, Dict, Tuple, List, FrozenSet, Optional

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
    distances = _distances(
        (src, ((dst, 1) for dst in dsts)) for src, (_, dsts) in ret.items()
    )
    return ret, distances


@Task(year=2022, day=16, task=1, extra_config={"actors": ["AA"], "total_time": 30})
def task01(data, log: Callable[[AnyStr], None], actors: List[str], total_time: int):
    system, distances = data
    best_flow = _find_flow(system=system, distances=distances, log=log, actors=actors, total_time=total_time)
    return best_flow


@Task(year=2022, day=16, task=2, extra_config={"actors": ["AA", "AA"], "total_time": 26})
def task02(data, log: Callable[[AnyStr], None], actors: List[str], total_time: int):
    system, distances = data
    best_flow = _find_flow(system=system, distances=distances, log=log, actors=actors, total_time=total_time)
    return best_flow


@dataclass(order=True, frozen=True)
class _SystemState:
    actors: Tuple[Tuple[str, int], ...]
    closed_valves: FrozenSet[str]
    total_flow: int
    total: int
    time: int


def _find_flow(
        system: Dict[str, Tuple[int, List[str]]],
        distances: Dict[Tuple[str, str], int],
        actors: List[str],
        total_time: int,
        log: Callable[[AnyStr], None],
):
    from tqdm import tqdm
    seen, max_seen = set(), 0
    heap = [
        (
            0,
            _SystemState(
                actors=tuple((x, 0) for x in actors),
                closed_valves=frozenset(src for src, (flow, _) in system.items() if flow > 0),
                total_flow=0,
                total=0,
                time=total_time,
            ),
        )
    ]

    log(f"Finding best flow that can be created by {len(actors)} actors in {total_time} minutes")
    log("\n".join(f"  -> {i + 1:{len(str(len(actors)))}d}. actor starts at {a}" for i, a in enumerate(actors)))

    with tqdm(desc="Testing paths", total=None, leave=False) as pb:
        while len(heap) > 0:
            pb.update()
            estimate, state = heapq.heappop(heap)
            estimate = -estimate
            if state in seen:
                continue
            seen.add(state)
            potential = estimate + sum(
                max(
                    (
                        system[valve][0] * (state.time - delta - 1)
                        for room, age in state.actors
                        if (delta := distances[room, valve] - age) in range(state.time)
                    ),
                    default=0,
                )
                for valve in state.closed_valves
            )
            if estimate > max_seen:
                max_seen = estimate
            if potential < max_seen:
                continue

            moves_by_time = defaultdict(lambda: defaultdict(list))
            for valve in state.closed_valves:
                for i, (room, age) in enumerate(state.actors):
                    delta = distances[room, valve] - age
                    if delta in range(state.time):
                        moves_by_time[delta][i].append(valve)
            if not moves_by_time:
                continue

            for delta, actor_moves in moves_by_time.items():
                indices: List[Optional[int]] = [None] * len(actors)
                while True:
                    for i, index in enumerate(indices):
                        index = 0 if index is None else index + 1
                        if index < len(actor_moves[i]):
                            indices[i] = index
                            break
                        indices[i] = None
                    else:
                        break
                    valves = [
                        (i, actor_moves[i][index])
                        for i, index in enumerate(indices)
                        if index is not None
                    ]
                    if len(valves) != len(set(valve for _, valve in valves)):
                        continue
                    new_rooms = [(room, age + delta + 1) for room, age in state.actors]
                    for i, valve in valves:
                        new_rooms[i] = valve, 0
                    rate = sum(system[valve][0] for _, valve in valves)
                    new_state = _SystemState(
                        actors=tuple(sorted(new_rooms)),
                        closed_valves=state.closed_valves - set(valve for _, valve in valves),
                        total_flow=state.total_flow + rate,
                        total=state.total + state.total_flow * (delta + 1),
                        time=state.time - delta - 1,
                    )
                    heapq.heappush(heap, (-estimate - rate * new_state.time, new_state))

    log(f"Best flow that can be created by {len(actors)} actors in {total_time} minutes is {max_seen}")

    return max_seen


def _distances(adj):
    keys, distances = set(), defaultdict(lambda: math.inf)
    for src, dsts in adj:
        keys.add(src)
        distances[src, src] = 0
        for dst, weight in dsts:
            keys.add(dst)
            distances[dst, dst] = 0
            distances[src, dst] = weight
    for mid in keys:
        for src in keys:
            for dst in keys:
                distance = distances[src, mid] + distances[mid, dst]
                if distance < distances[src, dst]:
                    distances[src, dst] = distance
    return distances
