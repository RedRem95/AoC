import queue
from typing import Any, Optional, List, Dict, Set, Tuple

from AoC_Companion.Day import Day, TaskResult


class Day12(Day):

    def __init__(self, year: int):
        super().__init__(year)

    def pre_process_input(self, data: Any) -> Any:
        data: List[str] = super().pre_process_input(data=data)
        data = [x for x in data if len(x) > 0]
        ret: Dict[str, Set[str]] = {}
        for line in data:
            line = line.strip()
            l1, l2 = line.split("-")
            if l1 not in ret:
                ret[l1] = set()
            if l2 not in ret:
                ret[l2] = set()
            ret[l1].add(l2)
            ret[l2].add(l1)
        return ret

    def run_t1(self, data: Dict[str, Set[str]]) -> Optional[TaskResult]:
        paths = self.find_way(system=data, start="start", target="end", special_rule=False)
        log = [
            f"The tunnel network has {len(data)} caves",
            f"  {sum(1 if str(x).isupper() else 0 for x in data.keys() if x not in ('start', 'end'))} are big",
            f"  {sum(0 if str(x).isupper() else 1 for x in data.keys() if x not in ('start', 'end'))} are small",
            f"There are {len(paths)} paths possible when you visit small caves only once"
        ]
        return TaskResult(len(paths), log=log)

    def run_t2(self, data: Dict[str, Set[str]]) -> Optional[TaskResult]:
        paths = self.find_way(system=data, start="start", target="end", special_rule=True)
        log = [
            f"The tunnel network has {len(data)} caves",
            f"  {sum(1 if str(x).isupper() else 0 for x in data.keys() if x not in ('start', 'end'))} are big",
            f"  {sum(0 if str(x).isupper() else 1 for x in data.keys() if x not in ('start', 'end'))} are small",
            f"There are {len(paths)} paths possible when you allow yourself to visit one small cave twice"
        ]
        return TaskResult(len(paths), log=log)

    @staticmethod
    def can_visit(cave: str, visited: List[str]) -> bool:
        return cave.isupper() or cave not in visited

    @staticmethod
    def can_visit_special(cave: str, visited: List[str]) -> Tuple[bool, bool]:
        if Day12.can_visit(cave=cave, visited=visited):
            return True, False
        lower_caves = [x for x in visited if x.islower()]
        if len(set(lower_caves)) == len(lower_caves) and cave not in ["start", "end"]:
            return True, True
        return False, False

    @staticmethod
    def find_way(system: Dict[str, Set[str]], start: str, target: str, special_rule: bool) -> Set[Tuple[str]]:

        sub_paths = queue.Queue()
        sub_paths.put(([start], not special_rule))
        ret: Set[Tuple[str]] = set()

        while not sub_paths.empty():
            sub_path, special_taken = sub_paths.get()
            sub_path: List[str]
            special_taken: bool
            for next_cave in system[sub_path[-1]]:
                _special_taken = special_taken
                if _special_taken and not Day12.can_visit(cave=next_cave, visited=sub_path):
                    continue
                elif not _special_taken:
                    can_visit, _special_taken = Day12.can_visit_special(cave=next_cave, visited=sub_path)
                    if not can_visit:
                        continue
                new_path = sub_path + [next_cave]
                if next_cave == target:
                    ret.add(tuple(new_path))
                else:
                    sub_paths.put((new_path, _special_taken))

        return ret
