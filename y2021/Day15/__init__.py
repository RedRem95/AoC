from typing import Any, Optional, List, Tuple, Set

import numpy as np
from AoC_Companion.Day import Day, TaskResult

from ..Day09 import Day09


class Day15(Day):

    def __init__(self, year: int):
        super().__init__(year)

    def pre_process_input(self, data: Any) -> Any:
        data: List[str] = super().pre_process_input(data=data)
        data = [x for x in data if len(x) > 0]
        ret = np.array([[int(y) for y in x] for x in data], dtype=np.uint8)
        return ret

    def run_t1(self, data: np.ndarray) -> Optional[TaskResult]:
        cost = self.find_path(data=data, start=(0, 0), finish=(data.shape[0] - 1, data.shape[1] - 1))
        return TaskResult(int(cost))

    def run_t2(self, data: np.ndarray) -> Optional[TaskResult]:
        factor = 5
        dw, dh = data.shape
        new_data = np.zeros(shape=(dw * factor, dh * factor), dtype=data.dtype)
        for i in range(factor):
            for j in range(factor):
                patch = data + i + j
                patch[patch > 9] = patch[patch > 9] - 9
                new_data[i * dw:(i + 1) * dw, j * dh:(j + 1) * dh] = patch

        # s_jonas_path = os.path.join(os.path.dirname(__file__), "Special_jonas.txt")
        # print(s_jonas_path)
        # with open(s_jonas_path, "wb") as f_out:
        #     for i in range(new_data.shape[0]):
        #         for j in range(new_data.shape[1]):
        #             f_out.write(f"{new_data[i, j]}".encode("utf-8"))
        #         f_out.write("\n".encode("utf-8"))
        # exit()

        cost = self.find_path(data=new_data, start=(0, 0), finish=(new_data.shape[0] - 1, new_data.shape[1] - 1))
        return TaskResult(int(cost))

    @staticmethod
    def find_path(
            data: np.ndarray, start: Tuple[int, int], finish: Tuple[int, int]
    ) -> Optional[int]:

        if not (Day09.pt_in_data(data=data, point=start) and Day09.pt_in_data(data=data, point=finish)):
            return None

        moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        a_matrix = np.zeros(shape=data.shape, dtype=float)
        a_matrix[:, :] = np.inf
        a_matrix[start[0], start[1]] = 0
        pos_positions: Set[Tuple[int, int]] = {start}

        def find_next_pos() -> Tuple[int, int]:
            ret = sorted((x for x in pos_positions), key=lambda x: a_matrix[x[0], x[1]])[0]
            pos_positions.remove(ret)
            return ret

        while True:
            pos = find_next_pos()
            cost = a_matrix[pos[0], pos[1]]
            if pos == finish:
                return cost

            for i, j in ((m1 + pos[0], m2 + pos[1]) for m1, m2 in moves):
                if not Day09.pt_in_data(data=data, point=(i, j)):
                    continue
                new_cost = cost + data[i, j]
                if new_cost < a_matrix[i, j]:
                    a_matrix[i, j] = new_cost
                    pos_positions.add((i, j))
