import functools
from typing import Any, Optional, List, Tuple, Callable

from AoC_Companion.Day import Day, TaskResult


class Day21(Day):
    _get_die = Callable[[int], int]

    def __init__(self, year: int):
        super().__init__(year)
        self._deterministic_die = 0
        self._rounds = 0

    def pre_process_input(self, data: Any) -> Any:
        data: List[str] = super().pre_process_input(data=data)
        data = [x for x in data if len(x) > 0]
        p1 = int(data[0].split(":")[-1])
        p2 = int(data[1].split(":")[-1])
        return p1, p2

    def run_t1(self, data: Tuple[int, int]) -> Optional[TaskResult]:
        points, rounds_played = self.play_game(
            start_p1=data[0], start_p2=data[1], die=self.roll_deterministic_die, target_points=1000
        )
        ret = points[rounds_played % len(points)] * rounds_played * 3
        return TaskResult(ret, log=[
            f"You played {rounds_played} rounds of 'Dirac Dice' with the fully deterministic die "
            f"and didnt split reality. WP",
            *[f"  player {i + 1} made {pts} points"
              f"{' <- Winner' if pts == max(points) else ''}" for i, pts in enumerate(points)]
        ])

    def run_t2(self, data: Tuple[int, int]) -> Optional[TaskResult]:
        wins: Tuple[int, int] = self.play_q_game(*data, 0, 0, True, 0, 0)
        num_realities = sum(wins)
        ret = max(wins)
        return TaskResult(ret, log=[
            f"While playing 'Dirac Dice' with the quantum die you split the reality in {num_realities} versions",
            *[f"  player {i + 1} won in {win}{' <- Winner' if win == ret else ''}" for i, win in enumerate(wins)]
        ])

    def roll_deterministic_die(self, times: int) -> int:
        ret = 0
        for _ in range(times):
            ret += self._deterministic_die + 1
            self._deterministic_die = (self._deterministic_die + 1) % 100
        return ret

    @staticmethod
    def play_game(start_p1: int, start_p2: int, die: _get_die, target_points) -> Tuple[Tuple[int, ...], int]:
        pos: List[int] = [start_p1, start_p2]
        points: List[int] = [0, 0]
        i = 0
        while all(p < target_points for p in points):
            pos[i % 2] = (pos[i % 2] + die(3))
            while pos[i % 2] > 10:
                pos[i % 2] -= 10
            points[i % 2] += pos[i % 2]
            i += 1

        return tuple(points), i

    @staticmethod
    def add_tuple(x: Tuple[int, ...], y: Tuple[int, ...]) -> Tuple[int, ...]:
        return tuple(a + b for a, b in zip(x, y))

    @staticmethod
    @functools.cache
    def play_q_game(
            position_p1: int, position_p2: int, score_p1: int, score_p2: int, turn_p1: bool, cur_roll: int, rolls: int
    ) -> Tuple[int, int]:
        if score_p1 >= 21:
            return 1, 0
        if score_p2 >= 21:
            return 0, 1
        out = (0, 0)
        if rolls != 3:
            for i in range(1, 4):
                out = Day21.add_tuple(
                    out,
                    Day21.play_q_game(position_p1, position_p2, score_p1, score_p2, turn_p1, cur_roll + i, rolls + 1)
                )
        else:
            cur = position_p1 if turn_p1 else position_p2
            cur += cur_roll
            cur = ((cur - 1) % 10) + 1
            if turn_p1:
                out = Day21.add_tuple(
                    out,
                    Day21.play_q_game(cur, position_p2, score_p1 + cur, score_p2, not turn_p1, 0, 0)
                )
            else:
                out = Day21.add_tuple(
                    out,
                    Day21.play_q_game(position_p1, cur, score_p1, score_p2 + cur, not turn_p1, 0, 0)
                )
        return out
