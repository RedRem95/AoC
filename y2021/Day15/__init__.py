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

    # noinspection PyUnresolvedReferences
    def run_t1(self, data: np.ndarray) -> Optional[TaskResult]:
        elements = int(np.prod(data.shape))
        log = []
        try:
            from scipy.sparse import lil_matrix
            from scipy.sparse.csgraph import dijkstra
            graph = lil_matrix((elements, elements), dtype=data.dtype)
            moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]

            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    el = self.pt_to_idx(i=i, j=j, n=data.shape[0])
                    for pi, pj in ((m1 + i, m2 + j) for m1, m2 in moves):
                        if not Day09.pt_in_data(data=data, point=(pi, pj)):
                            continue
                        pel = self.pt_to_idx(i=pi, j=pj, n=data.shape[0])
                        graph[el, pel] = data[pi, pj]
            dist_matrix = dijkstra(csgraph=graph, directed=True, indices=0, return_predecessors=False, min_only=True)
            cost = int(dist_matrix[-1])
            log.append("Using scipy dijkstra")
        except ImportError:
            cost = self.find_path(data=data, start=(0, 0), finish=(data.shape[0] - 1, data.shape[1] - 1))
            log.append("Using custom dijkstra")

        log.extend([
            f"Field has size of {data.shape[1]}x{data.shape[0]} => {elements} fields",
            f"The fastest way over the field costs {cost}"
        ])
        return TaskResult(cost, log=log)

    def run_t2(self, data: np.ndarray) -> Optional[TaskResult]:
        factor = 5
        dw, dh = data.shape
        new_data = np.zeros(shape=(dw * factor, dh * factor), dtype=data.dtype)
        for i in range(factor):
            for j in range(factor):
                patch = data + i + j
                patch[patch > 9] = patch[patch > 9] - 9
                new_data[i * dw:(i + 1) * dw, j * dh:(j + 1) * dh] = patch
        r = self.run_t1(data=new_data)
        return TaskResult(r.get_result(), log=r.get_log())

    @staticmethod
    def pt_to_idx(i: int, j: int, n: int) -> int:
        return i * n + j

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
