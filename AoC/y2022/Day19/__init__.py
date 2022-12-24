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
    "start_resources": {}, "start_robots": {"ore": 1}, "sim_steps": 24, "target": "geode",
})
def task01(data, log: Callable[[AnyStr], None], start_resources, start_robots, sim_steps, target):
    log(f"Simulating for {sim_steps} minutes to get max {target}")
    log(f"There are {len(data)} blueprints to choose from")
    log(f"\n".join(f'{k:4d}: {data[k]}' for k in sorted(data.keys())))
    ret = 0

    for blueprint_id, blueprint in data.items():
        blueprint: Blueprint
        realities = blueprint.sim_blueprint(
            time_steps=sim_steps, start_resources=start_resources, start_robots=start_robots, target=target
        )
        max_target = max(r[target] for r in realities)
        # best_resources = blueprint.sim_blueprint_rec(
        #     time_steps=sim_steps, resources=start_resources, robots=start_robots, no_robots=[], target=target,
        # )
        # max_target = best_resources[target]
        log(f"Blueprint {blueprint_id} produced at max {max_target} {target} in {sim_steps} minutes")
        ret += blueprint_id * max_target

    return ret


@Task(year=2022, day=19, task=2, extra_config={
    "start_resources": {}, "start_robots": {"ore": 1}, "max_id": 3, "sim_steps": 32, "target": "geode",
})
def task02(data, log: Callable[[AnyStr], None], start_resources, start_robots, max_id, sim_steps, target):
    log(f"Simulating for {sim_steps} minutes to get max {target}")
    data = {k: v for k, v in data.items() if k <= max_id}
    log(f"There are {len(data)} blueprints to choose from")
    log(f"\n".join(f'{k:4d}: {data[k]}' for k in sorted(data.keys())))

    ret = 1
    for blueprint_id, blueprint in data.items():
        blueprint: Blueprint
        realities = blueprint.sim_blueprint(
            time_steps=sim_steps, start_resources=start_resources, start_robots=start_robots
        )
        max_target = max(r[target] for r in realities)
        # best_resources = blueprint.sim_blueprint_rec(
        #     time_steps=sim_steps, resources=start_resources, robots=start_robots, no_robots=[], target=target,
        # )
        # max_target = best_resources[target]
        log(f"Blueprint {blueprint_id} produced at max {max_target} geodes in {sim_steps} minutes")
        ret = ret * max_target

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
            build_resources = {}
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

    def sim_blueprint_2(
            self, time_steps: int, start_resources: Dict[str, int], start_robots: Dict[str, int]
    ) -> List[Dict[str, int]]:
        from tqdm import tqdm

        realities: List[Tuple[Dict[str, int], Dict[str, int]]] = [
            (defaultdict(lambda: 0), defaultdict(lambda: 0))
        ]

        for k, v in start_resources.items():
            realities[0][0][k] += v
        for k, v in start_robots.items():
            realities[0][1][k] += v

        with tqdm(range(time_steps), total=time_steps, leave=False, desc="Simulating blueprint") as pb:
            for i in pb:
                pb.set_description(f"Simulating blueprint - {len(realities)} realities")
                new_realities: List[Tuple[Dict[str, int], Dict[str, int]]] = []
                for reality_resources, reality_robots in realities:
                    no_robots = []
                    could_build = []
                    should_build = []
                    for robot, robot_cost in self._robots.items():
                        if _can_build(resources=reality_resources, robot_cost=robot_cost):
                            could_build.append(robot)
                            if robot not in no_robots:
                                should_build.append(robot)
                    if any(robot not in could_build for robot in self._robots.keys()):
                        should_build.append(None)
                    for build in should_build:
                        new_resources = reality_resources.copy()
                        new_robots = reality_robots.copy()
                        if build is None:
                            pass
                        else:
                            for ore_c, ore_a in self._robots[build].items():
                                new_resources[ore_c] -= ore_a
                            new_robots[build] += 1
                        for robot_type, robot_amount in reality_robots.items():
                            new_resources[robot_type] += robot_amount
                        new_realities.append((new_resources, new_robots))
                realities = new_realities

        return [x[0] for x in realities]

    def sim_blueprint(
            self, time_steps: int, start_resources: Dict[str, int], start_robots: Dict[str, int], target: str,
    ) -> List[Dict[str, int]]:

        realities: _REALITIES_TYPE = [
            (defaultdict(lambda: 0), defaultdict(lambda: 0), time_steps)
        ]

        for k, v in start_resources.items():
            realities[0][0][k] += v
        for k, v in start_robots.items():
            realities[0][1][k] += v

        best_reality = defaultdict(lambda: 0)
        no_robots = []

        while len(realities) >= 0:
            realities = self._sanitize_sort_realities(realities)
            reality_resources, reality_robots, time_left = realities.pop(0)
            if time_left <= 0:
                if reality_resources[target] > best_reality[target]:
                    print(f"{best_reality[target]} -> {reality_resources[target]}")
                    best_reality = reality_resources
            could_build = []
            should_build = []
            for robot, robot_cost in self._robots.items():
                if _can_build(resources=reality_resources, robot_cost=robot_cost):
                    could_build.append(robot)
                    if robot not in no_robots:
                        should_build.append(robot)
            if any(robot not in could_build for robot in self._robots.keys()):
                should_build.append(None)
            for build in should_build:
                new_resources = reality_resources.copy()
                new_robots = reality_robots.copy()
                if build is None:
                    pass
                else:
                    for ore_c, ore_a in self._robots[build].items():
                        new_resources[ore_c] -= ore_a
                    new_robots[build] += 1
                for robot_type, robot_amount in reality_robots.items():
                    new_resources[robot_type] += robot_amount
                realities.append((new_resources, new_robots, time_left - 1))

        return [best_reality]

    def _sanitize_sort_realities(
            self, realities: _REALITIES_TYPE
    ) -> _REALITIES_TYPE:
        realities = sorted(realities, key=lambda x: x[-1])

        resources = [x[0] for x in realities]
        del_keys = []
        for i in range(len(realities) - 1):
            if realities[i][0] in resources[i + 1:]:
                del_keys.append(i)

        for k in del_keys[::-1]:
            del realities[k]

        return realities

    def sim_blueprint_rec(
            self, time_steps: int, resources: Dict[str, int], robots: Dict[str, int], no_robots: List[str], target: str,
    ) -> Dict[str, int]:
        if time_steps <= 0:
            return resources

        if not isinstance(resources, defaultdict):
            _tmp = resources
            resources = defaultdict(lambda: 0)
            for k, v in _tmp.items():
                resources[k] += v
        if not isinstance(robots, defaultdict):
            _tmp = robots
            robots = defaultdict(lambda: 0)
            for k, v in _tmp.items():
                robots[k] += v

        ret = defaultdict(lambda: 0)

        could_build = []
        should_build = []
        for robot, robot_cost in self._robots.items():
            if _can_build(resources=resources, robot_cost=robot_cost):
                could_build.append(robot)
                if robot not in no_robots:
                    should_build.append(robot)
        if any(robot not in could_build for robot in self._robots.keys()):
            should_build.append(None)
        for build in should_build:
            new_resources = resources.copy()
            new_robots = robots.copy()
            if build is None:
                pass
            else:
                for ore_c, ore_a in self._robots[build].items():
                    new_resources[ore_c] -= ore_a
                new_robots[build] += 1
            for robot_type, robot_amount in robots.items():
                new_resources[robot_type] += robot_amount
            best = self.sim_blueprint_rec(
                time_steps=time_steps - 1, resources=new_resources, robots=new_robots,
                no_robots=should_build if build is None else [], target=target,
            )
            if best[target] > ret[target]:
                ret = best
        return ret


def _can_build(resources: Dict[str, int], robot_cost: Dict[str, int]) -> bool:
    return all(resources[ore_c] >= ore_a for ore_c, ore_a in robot_cost.items())
