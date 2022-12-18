import enum
from typing import Callable, AnyStr, List, Tuple, Dict

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor


class _JetDirection(enum.Enum):
    Left = "<"
    Right = ">"

    def get_tuple(self) -> Tuple[int, int]:
        if self == self.__class__.Left:
            return -1, 0
        if self == self.__class__.Right:
            return 1, 0


_Rocks: List[List[Tuple[int, int]]] = [
    [(-1, 0), (0, 0), (1, 0), (2, 0)],
    [(0, 1), (-1, 0), (0, 0), (0, -1), (1, 0)],
    [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)],
    [(0, 2), (0, 1), (0, 0), (0, -1)],
    [(0, 0), (1, 0), (0, 1), (1, 1)],
]


@Preprocessor(year=2022, day=17)
def preproc_1(data):
    for line in data:
        line = line.strip()
        if len(line) <= 0:
            continue
        return [_JetDirection(x) for x in line]
    return None


@Task(year=2022, day=17, task=1, extra_config={
    "rocks": _Rocks, "cave_width": 7, "left_spawn": 2, "spawn_count": 2022, "spawn_height": 3
})
def task01(data, log: Callable[[AnyStr], None], rocks, cave_width, left_spawn, spawn_count, spawn_height):
    tower_height, spawned_rocks = _sim_rocks(
        cave_width=cave_width,
        left_spawn=left_spawn,
        spawn_count=spawn_count,
        spawn_height=spawn_height,
        rocks=rocks,
        winds=data,
        log=log,
        draw=False,
    )
    log(f"Spawned {spawned_rocks} rocks")
    return tower_height


@Task(year=2022, day=17, task=2, extra_config={
    "rocks": _Rocks, "cave_width": 7, "left_spawn": 2, "spawn_count": 1000000000000, "spawn_height": 3
})
def task02(data, log: Callable[[AnyStr], None], rocks, cave_width, left_spawn, spawn_count, spawn_height):
    winds = []
    for _ in range(100):
        winds.extend(data)
    winds = _find_pattern(pattern_list=winds)
    if len(winds) < len(data):
        log(f"Found pattern of length {len(winds)} vs {len(data)}")
    else:
        winds = data
        log(f"Did not find an alternative pattern")
    cave, spawned_rocks = _sim_rocks(
        cave_width=cave_width,
        left_spawn=left_spawn,
        spawn_count=spawn_count,
        spawn_height=spawn_height,
        rocks=rocks,
        winds=winds,
        log=log,
        draw=False,
    )
    tower_height = max([k[1] for k, v in cave.items() if v == 1] + [0])
    return tower_height


def _sim_rocks(
        cave_width: int, left_spawn: int, spawn_height: int, log: Callable[[str], None], spawn_count: int,
        rocks: List[List[Tuple[int, int]]], winds: List[_JetDirection], draw: bool,
) -> Tuple[int, int]:
    from tqdm import tqdm
    cave = {}

    rocks_meta = [(rock, _get_rock_meta(rock=rock)) for rock in rocks]
    tower_height = 0
    drop_height_collection = []
    j = 0
    for i in tqdm(range(spawn_count), total=spawn_count, desc="Falling rocks", unit="r", leave=False):
        rock, rock_meta = rocks_meta[i % len(rocks_meta)]
        spawn_pos = _spawn_position(tower_height=tower_height, left_spawn=left_spawn,
                                    spawn_height=spawn_height, rock_meta=rock_meta)
        falling_rocks = [_add_tpl(t1=spawn_pos, t2=rock_piece) for rock_piece in rock]
        current_drop_height = 0
        if draw:
            log(f"{'-' * 10}{i:^3d}{'-' * 10}")
            log(f"Spawn")
            _cave = cave.copy()
            _cave.update({k: 2 for k in falling_rocks})
            log(_draw_cave(_cave, cave_width=cave_width))
        while True:
            wind_direction = winds[j % len(winds)]
            _falling_rocks = [_add_tpl(t1=wind_direction.get_tuple(), t2=rock_piece) for rock_piece in falling_rocks]
            if all(0 <= x[0] < cave_width and x not in cave for x in _falling_rocks):
                falling_rocks = _falling_rocks
            if draw and True:
                log(f"After wind {wind_direction.name}")
                _cave = cave.copy()
                _cave.update({k: 2 for k in falling_rocks})
                log(_draw_cave(_cave, cave_width=cave_width))
            _falling_rocks = [_add_tpl(t1=(0, -1), t2=rock_piece) for rock_piece in falling_rocks]
            rocks_fixed = False
            if any(rock_piece in cave or rock_piece[1] <= 0 for rock_piece in _falling_rocks):
                rocks_fixed = True
                cave.update({k: 1 for k in falling_rocks})
                falling_rocks = []
                tower_height = max([k[1] for k, v in cave.items() if v == 1] + [0])
                drop_height_collection.append(current_drop_height)
            else:
                falling_rocks = _falling_rocks
                current_drop_height += 1
            if draw and True:
                log(f"After drop")
                _cave = cave.copy()
                _cave.update({k: 2 for k in falling_rocks})
                log(_draw_cave(_cave, cave_width=cave_width))
            j += 1
            if rocks_fixed:
                break
        pattern_list = _find_pattern(drop_height_collection)
        if len(pattern_list) != len(drop_height_collection):
            log(f"{len(pattern_list)}, {len(drop_height_collection)}")
            exit()

    return max([k[1] for k, v in cave.items() if v == 1] + [0]), spawn_count


def _add_tpl(t1: Tuple[int, int], t2: Tuple[int, int]) -> Tuple[int, int]:
    return t1[0] + t2[0], t1[1] + t2[1]


def _get_rock_meta(rock: List[Tuple[int, int]]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    min_x, max_x = min(x[0] for x in rock), max(x[0] for x in rock)
    min_y, max_y = min(x[1] for x in rock), max(x[1] for x in rock)
    return (min_x, max_x), (min_y, max_y)


def _draw_cave(cave: Dict[Tuple[int, int], int], cave_width: int) -> str:
    symbol = {
        -1: ".",
        0: "-",
        1: "#",
        2: "@",
    }
    min_x, max_x = 0, cave_width
    min_y, max_y = 0, max(x[1] for x in cave.keys())

    ret = []
    for y in range(max_y, min_y, -1):
        line = ["|"]
        for x in range(min_x, max_x, 1):
            pt = (x, y)
            cave_element = cave.get(pt, -1)
            line.append(symbol[cave_element][:1])
        line.append("|")
        ret.append("".join(line))
    ret.append(f"+{'-' * (max_x - min_x)}+")
    return "\n".join(ret)


def _spawn_position(
        tower_height: int,
        left_spawn: int,
        spawn_height: int,
        rock_meta: Tuple[Tuple[int, int], Tuple[int, int]],
) -> Tuple[int, int]:
    return left_spawn - rock_meta[0][0], tower_height + spawn_height - rock_meta[1][0] + 1


def _find_pattern(pattern_list: List) -> List:
    for i in range(1, len(pattern_list), 1):
        if len(pattern_list) % i == 0:
            chunks = [pattern_list[j*i:(j+1)*i] for j in range(len(pattern_list) // i)]
            if all(chunks[0] == chunk for chunk in chunks[1:]):
                return chunks[0]

    return pattern_list
