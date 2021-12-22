import itertools
from collections import Counter
from typing import Any, Optional, List, Tuple, Callable, Set, Union, Iterable

import numpy as np
from AoC_Companion.Day import Day, TaskResult


class Day22(Day):
    _coord_range = Tuple[int, int]
    _operation = Tuple[bool, _coord_range, _coord_range, _coord_range]

    def __init__(self, year: int):
        super().__init__(year)

    def pre_process_input(self, data: Any) -> Any:
        data: List[str] = super().pre_process_input(data=data)
        data = [x for x in data if len(x) > 0]
        ret: List[Day22._operation] = []
        for line in data:
            line = line.strip()
            op = True if line.split(" ")[0].strip() == "on" else False
            ranges = line.split(" ")[1].strip()
            x_r, y_r, z_r = ranges.split(",")
            ranges = []
            for r in (x_r, y_r, z_r):
                r: str = r.split("=")[-1]
                ranges.append((int(r.split("..")[0]), int(r.split("..")[1])))
            # noinspection PyTypeChecker
            ret.append((op, *ranges))
        return ret

    def run_t1(self, data: List[_operation]) -> Optional[TaskResult]:
        small_range: Tuple[int, int] = (-50, 50)
        ranges: List[Tuple[int, int]] = [small_range for _ in range(len(data[0]) - 1)]
        return self._run(ranges=ranges, ops=data, sim_method=self.sim_reactor_fast)

    def run_t2(self, data: List[_operation]) -> Optional[TaskResult]:
        return self._run(ops=data, sim_method=self.sim_reactor_fast)

    @staticmethod
    def _run(
            ops: List[_operation], sim_method: Callable[[Optional[Tuple[Tuple[int, int], ...]],
                                                         List[_operation], Optional[List[str]]], Union[int, "Area"]],
            ranges: Optional[Iterable[_coord_range]] = None
    ) -> TaskResult:
        log = [f"Using {len(ops)} potential operations", "Restricting reactor ranges to"]
        if ranges is None:
            log.append("Reactor activatiion sequence is in unrestriced mode. Every cube is available")
            log.append("UNLIMITED POWAAAAAAAAAAAAAAAAAAA")
        else:
            c = {0: "x", 1: "y", 2: "z"}
            for i, r in enumerate(ranges):
                log.append(f"  {c.get(i, '_')} from {r[0]} to {r[1]}")
        ret = int(sim_method(ranges, ops, log))
        if ranges is None:
            full_area = "<ERROR>"
            percentage = full_area
        else:
            full_area = np.prod([max(r) - min(r) for r in ranges])
            percentage = f"{(ret / full_area) * 100:6.2f}"
        log.append(f"In the end {ret} cubes are on")
        log.append(f"  That is {percentage}% [{ret}/{full_area}]")
        log.append(f"  of the cubic area around the reactor")
        return TaskResult(ret, log=log)

    @staticmethod
    def sim_reactor(ranges: Optional[Iterable[_coord_range]], ops: List[_operation], log: List[str] = None) -> "Area":
        if ranges is not None:
            ranges = list(ranges)
        if log is None:
            log = []
        import tqdm

        reactor_on: Area = Area()

        for op, *bounds in tqdm.tqdm(ops, desc="Applying operations", leave=False, unit="o"):
            if ranges is not None:
                bounds = tuple(Day22.adjust_range(r=b, max_shape=r, offset=0) for b, r in zip(bounds, ranges))
            if any(b is None for b in bounds):
                continue
            patch = Patch(*bounds)
            if op:
                reactor_on.add(patch=patch)
                pass
            else:
                reactor_on.remove(patch=patch)
                pass

        log.append(f"In the end the reactor was 'split' into {len(reactor_on)} parts")

        return reactor_on

    @staticmethod
    def sim_reactor_fast(ranges: Optional[Iterable[_coord_range]], ops: List[_operation], log: List[str] = None) -> int:
        if ranges is not None:
            ranges = list(ranges)
        cuboid_signs = Counter()

        for op, *bounds in ops:
            if ranges is not None:
                bounds = tuple(Day22.adjust_range(r=b, max_shape=r, offset=0) for b, r in zip(bounds, ranges))
            if any(b is None for b in bounds):
                continue
            bounds = tuple((b[0], b[1]) for b in bounds)
            patch = Patch(*bounds)

            updates = Counter()
            for compare_patch, counted in cuboid_signs.items():
                intersection = Patch.find_overlap(patch1=compare_patch, patch2=patch)
                if intersection is not None:
                    updates[intersection] -= counted

            if op == 1:
                updates[patch] += 1

            cuboid_signs.update(updates)

        log.append(f"In the end {len(cuboid_signs.keys())} patches were registered and counted")

        return sum(patch.get_size() * counted for patch, counted in cuboid_signs.items())

    @staticmethod
    def adjust_range(r: _coord_range, offset: int, max_shape: Tuple[int, int]) -> Optional[_coord_range]:
        _adjusted: Tuple[int, ...] = tuple(_x - offset for _x in r)
        if _adjusted[0] > max_shape[1] or _adjusted[1] < max_shape[0]:
            return None
        _adjusted = tuple(min(max(_x, max_shape[0]), max_shape[1]) for _x in _adjusted)
        # noinspection PyTypeChecker
        return _adjusted


class Patch:
    def __init__(self, *bounds: Tuple[int, int]):
        self.bounds = tuple((min(x), max(x)) for x in bounds)

    def get_size(self) -> int:
        return int(np.prod([max(b) - min(b) + 1 for b in self.bounds]))

    def __eq__(self, other):
        if not isinstance(other, Patch):
            return False
        return self.bounds == other.bounds

    def __str__(self, with_size: bool = True):
        return f"Patch<{', '.join('..'.join(str(y) for y in x) for x in self.bounds)}" \
               f"{f' => {self.get_size()}' if with_size else ''}>"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.bounds)

    @classmethod
    def combine(cls, patch1: "Patch", patch2: "Patch") -> Optional["Patch"]:
        if cls.intersect(patch1=patch1, patch2=patch2):
            return None
        same_axis = [1 if b1 == b2 else 0 for b1, b2 in zip(patch1.bounds, patch2.bounds)]
        not_same_index = same_axis.index(0)
        if sum(same_axis) != len(same_axis) - 1:
            return None
        elif abs(patch1.bounds[not_same_index][0] - patch2.bounds[not_same_index][1]) == 1 or abs(
                patch1.bounds[not_same_index][1] - patch2.bounds[not_same_index][0]) == 1:
            bounds = [(min(b1[0], b2[0]), max(b1[1], b2[1])) for b1, b2 in zip(patch1.bounds, patch2.bounds)]
            return Patch(*bounds)
        return None

    @classmethod
    def intersect(cls, patch1: "Patch", patch2: "Patch") -> bool:
        if len(patch1.bounds) != len(patch2.bounds):
            return False

        return all(
            p1b[0] <= p2b[1] and p1b[1] >= p2b[0] for p1b, p2b in zip(patch1.bounds, patch2.bounds)
        )

    @classmethod
    def find_overlap(cls, patch1: "Patch", patch2: "Patch") -> Optional["Patch"]:
        if not cls.intersect(patch1=patch1, patch2=patch2):
            return None

        overlap = [(max(p1b[0], p2b[0]), min(p1b[1], p2b[1])) for p1b, p2b in zip(patch1.bounds, patch2.bounds)]
        return Patch(*overlap)

    @classmethod
    def subtract(cls, base: "Patch", take_away: "Patch") -> Set["Patch"]:

        bad_part = cls.find_overlap(base, take_away)
        if bad_part is None:
            return {base}
        if bad_part == base:
            return set()

        dim_collection: List[List[Tuple[int, int]]] = [[]]
        for dim in range(len(base.bounds)):
            new_dim_collection = []
            if base.bounds[dim][0] < bad_part.bounds[dim][0]:
                for dc in dim_collection:
                    new_dim_collection.append([*dc, (base.bounds[dim][0], bad_part.bounds[dim][0] - 1)])
            for dc in dim_collection:
                new_dim_collection.append([*dc, (bad_part.bounds[dim][0], bad_part.bounds[dim][1])])
            if base.bounds[dim][1] > bad_part.bounds[dim][1]:
                for dc in dim_collection:
                    new_dim_collection.append([*dc, (bad_part.bounds[dim][1] + 1, base.bounds[dim][1])])
            dim_collection = new_dim_collection

        ret = {Patch(*d) for d in dim_collection}
        ret = {x for x in ret if not cls.intersect(patch1=take_away, patch2=x)}

        joined_patches = list(ret)
        while True:
            found = False
            for i, j in itertools.combinations(range(len(joined_patches)), 2):
                combination = cls.combine(patch1=joined_patches[i], patch2=joined_patches[j])
                if combination is not None:
                    del joined_patches[j]
                    del joined_patches[i]
                    joined_patches.append(combination)
                    found = True
                    break
            if found:
                continue
            break

        return set(joined_patches)

    @classmethod
    def join(cls, *patches: "Patch") -> Set["Patch"]:
        if len(patches) <= 1:
            return {patches[0]}
        elif len(patches) == 2:
            patch1, patch2 = patches

            p1_wo_p2 = cls.subtract(base=patch1, take_away=patch2)
            return p1_wo_p2.union({patch2})
        else:
            working_patches = list(patches)
            while True:
                found = False
                for i, j in itertools.combinations(range(len(working_patches)), 2):
                    joined = cls.join(working_patches[i], working_patches[j])
                    if joined != {working_patches[i], working_patches[j]}:
                        del working_patches[j]
                        del working_patches[i]
                        working_patches = list(joined.union(working_patches))
                        found = True
                        break
                if found:
                    continue
                break

            return set(working_patches)


class Area:

    def __init__(self):
        self.patches: Set[Patch] = set()

    def get_size(self) -> int:
        return sum(p.get_size() for p in self.patches)

    def add(self, patch: Patch) -> "Area":
        self.patches = Patch.join(*self.patches, patch)
        return self

    def remove(self, patch: Patch) -> "Area":
        new_patches = set()
        for p in self.patches:
            new_patches.update(Patch.subtract(base=p, take_away=patch))
        self.patches = new_patches
        return self

    def __str__(self):
        return f"Area of {', '.join(p.__str__(with_size=False) for p in self.patches)} => {self.get_size()}"

    def __len__(self):
        return len(self.patches)

    def __int__(self):
        return self.get_size()
