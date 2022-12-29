import math
from collections import defaultdict
from typing import Callable, AnyStr, Dict, List, Tuple

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022, day=19)
def preproc_1(data):
    ret = {}
    for line in data:
        line = line.strip()
        if len(line) <= 0:
            continue
        b_id, b_data = line.split(":")
        b_id = int(b_id.strip().split(" ")[-1])
        if b_id in ret:
            raise Exception()
        ret[b_id] = Blueprint(line=b_data)
    return ret


@Task(year=2022, day=19, task=1, extra_config={
    "start_resources": {}, "start_robots": {"ore": 1}, "sim_steps": 24, "target": "geode", "with_progress": True
})
def task01(data, log: Callable[[AnyStr], None], start_resources, start_robots, sim_steps, target, with_progress):
    geode_count = _run(
        data=data, log=log, start_resources=start_resources,
        start_robots=start_robots, sim_steps=sim_steps, target=target, with_progress=with_progress
    )
    return sum(i * g for i, g in geode_count.items())


@Task(year=2022, day=19, task=2, extra_config={
    "start_resources": {}, "start_robots": {"ore": 1}, "sim_steps": 32, "target": "geode", "with_progress": True,
    "m_id": 3
})
def task02(data, log: Callable[[AnyStr], None], start_resources, start_robots, m_id, sim_steps, target, with_progress):
    geode_count = _run(
        data={k: v for k, v in data.items() if k <= m_id}, log=log, start_resources=start_resources,
        start_robots=start_robots, sim_steps=sim_steps, target=target, with_progress=with_progress
    )
    return math.prod(geode_count.values())


def _run(
        data, log: Callable[[AnyStr], None], start_resources, start_robots, sim_steps, target, with_progress
) -> Dict[int, int]:
    log(f"Simulating for {sim_steps} minutes to get max {target}")
    log(f"There are {len(data)} blueprints to choose from")
    # log(f"\n".join(f'{k:4d}: {data[k]}' for k in sorted(data.keys())))
    ret = {}

    p_lines = []
    if with_progress:
        from tqdm import tqdm
        pb = tqdm(data.items(), desc="Simulating blueprints", total=len(data), leave=False, unit="b")
        log2 = lambda _s: p_lines.append(_s)
    else:
        pb = data.items()
        log2 = log

    for blueprint_id, blueprint in pb:
        blueprint: Blueprint
        max_target = blueprint.sim_blueprint(
            time_steps=sim_steps, start_resources=start_resources, start_robots=start_robots, target=target
        )
        log2(f" -> Blueprint {blueprint_id:{len(str(max(data.keys())))}d} "
             f"produced at max {max_target:2d} {target} in {sim_steps} minutes")
        ret[blueprint_id] = max_target

    if len(p_lines) > 0:
        log("\n".join(str(x) for x in p_lines))

    return ret


_REALITIES_TYPE = List[Tuple[Dict[str, int], Dict[str, int], int]]


class Blueprint:

    def __init__(self, line: str):
        self._robots: Dict[str, Dict[str, int]] = {}
        robots = [x.strip() for x in line.split(".") if len(x.strip()) > 0]
        # Each obsidian robot costs 3 ore and 14 clay
        for robot in robots:
            robot_line_split = robot.split(" ", 4)
            robot_type = robot_line_split[1]
            build_resources = defaultdict(lambda: 0)
            for resource in robot_line_split[4].split("and"):
                resource = resource.strip()
                num, res = resource.split(" ")
                if res in build_resources:
                    raise Exception()
                build_resources[res] = int(num)
            if robot_type in self._robots:
                raise Exception()
            self._robots[robot_type] = build_resources

    def __str__(self):
        robot_cost_str = []
        for robot_type, robot_cost in self._robots.items():
            robot_cost_str.append(f"{robot_type}-Robot costs {' and '.join(f'{v} {k}' for k, v in robot_cost.items())}")
        return f"Blueprint has {len(self._robots)} robots: {', '.join(robot_cost_str)}"

    def sim_blueprint(
            self, time_steps: int, start_resources: Dict[str, int], start_robots: Dict[str, int], target: str,
    ) -> int:
        max_resource_cost = {}
        for costs in self._robots.values():
            for resource, cost in costs.items():
                max_resource_cost[resource] = max(max_resource_cost.get(resource, 0), cost)
        realities: _REALITIES_TYPE = [
            (defaultdict(lambda: 0), defaultdict(lambda: 0), time_steps)
        ]

        for k, v in start_resources.items():
            realities[0][0][k] += v
        for k, v in start_robots.items():
            realities[0][1][k] += v

        best_target = -1

        while len(realities) > 0:
            reality_resources, reality_robots, remain_time = realities.pop(0)
            if remain_time < 0:
                continue

            future_target = reality_resources[target] + (reality_robots[target] * remain_time)
            if future_target > best_target:
                best_target = future_target

            if remain_time > 0:
                prediction = self._optimal(resources=reality_resources, robots=reality_robots, sim_time=remain_time)
                if prediction[target] < best_target:
                    continue
                    pass

                for robot, robot_cost in self._robots.items():
                    if robot in max_resource_cost and reality_robots[robot] >= max_resource_cost[robot]:
                        # We dont need more of this robot xD
                        continue
                    demand = (robot_cost[material] - reality_resources[material] for material in self._robots.keys())
                    supply = (reality_robots[material] for material in self._robots.keys())
                    needed_time = max(
                        0 if d <= 0 else math.inf if s <= 0 else (d + s - 1) // s for d, s in zip(demand, supply)
                    )
                    needed_time += 1
                    if needed_time > remain_time:
                        continue
                    new_resources = reality_resources.copy()
                    for r, c in reality_robots.items():
                        new_resources[r] += c * needed_time
                    for r, c in robot_cost.items():
                        new_resources[r] -= c
                    new_robots = reality_robots.copy()
                    new_robots[robot] += 1
                    realities.append((new_resources, new_robots, remain_time - needed_time))

        return best_target

    def _optimal(self, resources: Dict[str, int], robots: Dict[str, int], sim_time: int):
        additional_robots = defaultdict(lambda: 0)
        potential_materials = defaultdict(lambda: 0, resources)
        for _ in range(sim_time):
            for robot in robots:
                potential_materials[robot] += robots[robot] + additional_robots[robot]
            for robot, costs in self._robots.items():
                if all(
                        potential_materials[material] >= cost * (additional_robots[robot] + 1)
                        for material, cost in costs.items()
                ):
                    additional_robots[robot] += 1
        return potential_materials
