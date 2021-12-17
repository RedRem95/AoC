from typing import Any, Optional, List, Tuple

import numpy as np
from AoC_Companion.Day import Day, TaskResult


class Day17(Day):
    _pt_type = np.ndarray

    def __init__(self, year: int):
        super().__init__(year)

    def pre_process_input(self, data: Any) -> Tuple[_pt_type, _pt_type]:
        data: List[str] = super().pre_process_input(data=data)
        line = [x for x in data if len(x) > 0][0].split(":")[-1]
        x_data, y_data = line.split(", ")
        x_min, x_max = x_data.split("=")[-1].split("..")
        y_min, y_max = y_data.split("=")[-1].split("..")

        return np.array((int(x_min), int(x_max))), np.array((int(y_min), int(y_max)))

    def run_t1(self, data: Tuple[_pt_type, _pt_type]) -> Optional[TaskResult]:
        paths = self.simulate_probe(initial=np.array((0, 0)), target_area=data, first=True)
        max_y = -np.inf
        for path in paths:
            max_y = max([max_y] + [pos[1] for pos in path])
        return TaskResult(max_y)

    def run_t2(self, data: Tuple[_pt_type, _pt_type]) -> Optional[TaskResult]:
        paths = self.simulate_probe(initial=np.array((0, 0)), target_area=data, first=False)
        return TaskResult(len(paths))

    @staticmethod
    def simulate_probe(initial: _pt_type, target_area: Tuple[_pt_type, _pt_type], first: bool) -> List[List[_pt_type]]:

        ret: List[List[Day17._pt_type]] = []
        offset: Day17._pt_type = initial.copy()
        initial -= offset
        target_x, target_y = target_area
        target_x -= offset[0]
        target_y -= offset[1]

        x_direction = np.sign(target_x)
        mirror = np.ones_like(offset)
        if (x_direction < 0).all():
            mirror[0] = -1
        target_x *= mirror[0]

        min_x = 0
        max_x = np.amax(target_x)

        min_y = np.amin(target_y)
        max_y = max(1000, min_y)

        possible_x = np.arange(start=min_x, stop=max_x + 1, step=1, dtype=int)
        possible_y = np.arange(start=min_y, stop=max_y + 1, step=1, dtype=int)
        change = np.ones_like(offset) * -1

        for j in reversed(range(possible_y.shape[0])):
            for i in range(possible_x.shape[0]):
                current_speed = np.array((possible_x[i], possible_y[j]))
                current_position: Day17._pt_type = initial.copy()

                current_path = [current_position.copy()]

                while Day17.can_still_hit(position=current_position, target_area=(target_x, target_y),
                                          speed=current_speed):
                    current_position += current_speed
                    current_path.append(current_position.copy())
                    current_speed += change
                    if current_speed[0] < 0:
                        current_speed[0] = 0
                    if Day17.in_target(position=current_position, target_area=(target_x, target_y)):
                        ret.append(current_path)
                        break
                if first and len(ret) > 0:
                    break
            if first and len(ret) > 0:
                break

        return [[y * mirror + offset for y in x] for x in ret]

    @staticmethod
    def in_target(position: _pt_type, target_area: Tuple[_pt_type, _pt_type]) -> bool:
        return all(np.amin(target_area[i]) <= position[i] <= np.amax(target_area[i]) for i in range(position.shape[0]))

    @staticmethod
    def can_still_hit(position: _pt_type, target_area: Tuple[_pt_type, _pt_type], speed: _pt_type) -> bool:
        target_x, target_y = target_area
        if position[0] > np.amax(target_x):
            return False
        if speed[0] == 0 and position[0] < np.amin(target_x):
            return False
        if speed[1] < 0 and position[1] < np.amin(target_y):
            return False

        return True
