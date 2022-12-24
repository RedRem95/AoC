from collections import defaultdict
from typing import Callable, AnyStr, List, Tuple, Set, Optional, Dict

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022, day=23)
def preproc_1(data: List[str]):
    ret: List["Elf"] = []
    i = 0
    for line in data:
        line = line.strip()
        if len(line) <= 0:
            continue
        for j, c in enumerate(line):
            if c == "#":
                ret.append(Elf(pos=(j, i)))
            elif c == ".":
                pass
            else:
                raise Exception()
        i += 1
    return ret


@Task(year=2022, day=23, task=1)
def task01(data: List["Elf"], log: Callable[[AnyStr], None]):
    i = _sim_elves(elves=data, log=log, max_rounds=10)
    width, height = _calc_area(elves=data)
    ret = (width * height) - len(data)
    log(f"After {i} rounds the elves span an area of {width}x{height} with {ret} empty spaces")

    return ret


@Task(year=2022, day=23, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    import sys
    i = _sim_elves(elves=data, log=log, max_rounds=sys.maxsize)
    width, height = _calc_area(elves=data)
    log(f"After {i} rounds the elves span an area of {width}x{height} with {(width * height) - len(data)} empty spaces")
    return i


def _calc_area(elves: List["Elf"]) -> Tuple[int, int]:
    min_x, max_x = min(x.pos[0] for x in elves), max(x.pos[0] for x in elves)
    min_y, max_y = min(x.pos[1] for x in elves), max(x.pos[1] for x in elves)
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    return width, height


def _sim_elves(elves: List["Elf"], max_rounds: int, log: Callable[[AnyStr], None]) -> int:
    log(f"There are {len(elves)} elves")
    i = 0
    while True:
        elf_positions = set(x.pos for x in elves)
        proposed_moves: Dict[Tuple[int, int], List["Elf"]] = defaultdict(list)

        for elf in elves:
            proposed_move = elf.propose_move(positions=elf_positions)
            if proposed_move is not None:
                proposed_moves[proposed_move].append(elf)

        elves_moved = 0
        for proposed_move, elfs in proposed_moves.items():
            if len(elfs) == 1:
                elfs[0].pos = proposed_move
                elves_moved += 1

        i += 1
        if elves_moved <= 0 or i >= max_rounds:
            log(f"Simulation took {i} rounds. In the last round {elves_moved} elves moved")
            return i


class Elf:

    def __init__(self, pos: Tuple[int, int]):
        self.pos = pos
        self._move_queue: List[Tuple[List[Tuple[int, int]], Tuple[int, int]]] = [
            ([(0, -1), (1, -1), (-1, -1)], (0, -1)),
            ([(0, 1), (1, 1), (-1, 1)], (0, 1)),
            ([(-1, 0), (-1, 1), (-1, -1)], (-1, 0)),
            ([(1, 0), (1, 1), (1, -1)], (1, 0)),
        ]

    def propose_move(self, positions: Set[Tuple[int, int]]) -> Optional[Tuple[int, int]]:

        def _tpl_add(t1: Tuple[int, int], t2: Tuple[int, int]) -> Tuple[int, int]:
            return t1[0] + t2[0], t1[1] + t2[1]

        ret = None
        found_any = False
        for i in range(len(self._move_queue)):
            check, move = self._move_queue[i]
            if any(_tpl_add(t1=self.pos, t2=c) in positions for c in check):
                found_any = True
            elif ret is None:
                ret = _tpl_add(t1=self.pos, t2=move)
        _tmp = self._move_queue.pop(0)
        self._move_queue.append(_tmp)
        return ret if found_any else None

    @classmethod
    def propose_helper(cls, elf: "Elf", positions: Set[Tuple[int, int]]) -> Tuple["Elf", Optional[Tuple[int, int]]]:
        return elf, elf.propose_move(positions=positions)


def _draw(data: List[Elf]) -> str:
    ret = []
    elf_positions = set(x.pos for x in data)
    for y in range(min(x[1] for x in elf_positions), max(x[1] for x in elf_positions) + 1, 1):
        line = []
        for x in range(min(x[0] for x in elf_positions), max(x[0] for x in elf_positions) + 1, 1):
            if (x, y) in elf_positions:
                line.append("#")
            else:
                line.append(".")
        ret.append("".join(line))
    return "\n".join(ret)
