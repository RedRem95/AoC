from enum import Enum
from typing import Dict, Tuple, Optional, Iterable, List

import numpy as np


class Orientation(Enum):
    ROW = 0,
    COLUMN = 1


class BingoGame:
    def __init__(self, data: np.ndarray):
        if len(data.shape) != 2:
            raise ValueError()
        if data.shape[0] != data.shape[1]:
            raise ValueError(f"Shapes do not align {data.shape[0]} != {data.shape[1]}")

        self._map: Dict[int, Tuple[int, int]] = {}
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                pos = (i, j)
                num = data[i, j]
                if num in self._map:
                    raise ValueError()
                self._map[num] = pos

        self._board = np.zeros(shape=data.shape, dtype=bool)

    def get_board(self) -> np.ndarray:
        data = np.zeros(shape=self._board.shape, dtype=int)
        for num, pos in self._map.items():
            data[pos[0], pos[1]] = num
        return data

    def check_win(self) -> Optional[Tuple[Orientation, int]]:
        for i in range(self._board.shape[0]):
            if np.all(self._board[i, :]):
                return Orientation.ROW, i
            if np.all(self._board[:, i]):
                return Orientation.COLUMN, i
        return None

    def calc_score(self, num: int) -> Optional[int]:
        win = self.check_win()
        if win is not None:
            data = self.get_board()
            score = np.sum(data[self._board != True])
            return score * num
        return None

    def mark_number(self, num: int) -> Optional[int]:
        if num in self._map:
            pos = self._map[num]
            self._board[pos[0], pos[1]] = True
        return self.calc_score(num=num)

    @staticmethod
    def play_bingo(draw_nums: List[int], *bingos: "BingoGame") -> Iterable[Tuple["BingoGame", int, int, int]]:
        for j, num in enumerate(draw_nums):
            for i, bingo in enumerate(bingos):
                if bingo.check_win() is not None:
                    continue
                score = bingo.mark_number(num=num)
                if score is not None:
                    yield bingo, score, i, j
