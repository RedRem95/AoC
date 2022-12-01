from typing import Callable, AnyStr, List, Any, Optional

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

from .bingo_game import BingoGame


@Preprocessor(year=2021, day=4)
def pre_process_input(data: Any) -> Any:
    data = data + [""]
    draw_nums = [int(x.strip()) for x in data[0].split(",")]
    bingos = []
    tmp_data = []
    for i in range(2, len(data)):
        line = data[i].strip()
        if len(line) > 0:
            tmp_data.append([int(x.strip()) for x in line.split(" ") if len(x) > 0])
        else:
            if len(tmp_data) > 0:
                bingos.append(BingoGame(data=np.array(tmp_data, dtype=int)))
                tmp_data = []
    return draw_nums, bingos


@Task(year=2021, day=4, task=1)
def run_t1(data: Any, log) -> Any:
    return _run(draw_nums=data[0], bingos=data[1], first_wins=True, log=log)


@Task(year=2021, day=4, task=2)
def run_t2(data: Any, log) -> Any:
    return _run(draw_nums=data[0], bingos=data[1], first_wins=False, log=log)


def _run(draw_nums: List[int], bingos: List[BingoGame], log, first_wins: bool = True):
    final_score: Optional[int] = None
    bingo: Optional[BingoGame] = None
    score: int = -1
    i: int = len(bingos) + 1
    j: int = len(draw_nums) + 1
    for bingo, score, i, j in BingoGame.play_bingo(draw_nums, *bingos):
        if first_wins:
            break
    if bingo is None:
        log("No winner found")
        return None
    log("\n".join([
        f"There are {len(draw_nums)} numbers generated to draw",
        f"There are {len(bingos)} bingo games created",
        f"The {i}. board won last on {j}. number",
        f"  The {j}. number was {draw_nums[j]}",
        f"  The board score was {score}"
    ]))
    return score
