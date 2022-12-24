from typing import Callable, AnyStr, Dict, Tuple, Union, List, Set

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor
from tqdm import tqdm

_MAP_TYPE = Dict[Tuple[int, int], bool]
_INSTRUCTION_TYPE = Union[str, int]
_INSTR_LIST = List[_INSTRUCTION_TYPE]
_PARTNER_DICT = Dict[
    Tuple[int, int], Tuple[Callable[[Tuple[int, int], Tuple[int, int]], Tuple[int, int]], Tuple[int, int]]]


@Preprocessor(year=2022, day=22)
def preproc_1(data):
    m: _MAP_TYPE = {}
    instructions: _INSTR_LIST = []
    i = 0
    while len(_ := data[i].rstrip()) <= 0:
        i += 1
    offset = i

    while len(line := data[i].rstrip()) > 0:
        for j, c in enumerate(line):
            if c == ".":
                m[(j, i - offset)] = True
            if c == "#":
                m[(j, i - offset)] = False
        i += 1

    while len(_ := data[i].rstrip()) <= 0:
        i += 1

    num_coll = []
    for c in data[i].upper().strip():
        if c in ("L", "R"):
            if len(num_coll) > 0:
                instructions.append(int("".join(num_coll)))
            num_coll = []
            instructions.append(c)
        else:
            num_coll.append(c)
    if len(num_coll) > 0:
        instructions.append(int("".join(num_coll)))

    return m, instructions


@Task(year=2022, day=22, task=1, extra_config={"draw": True})
def task01(data, log: Callable[[AnyStr], None], draw: bool):
    data: Tuple[_MAP_TYPE, _INSTR_LIST]
    m, instructions = data

    min_y = min(x[1] for x in m.keys() if any(m[y] is True for y in m.keys() if y[1] == x[1]))
    min_x = min(x[0] for x in m.keys() if x[1] == min_y and m[x] is True)
    current = (min_x, min_y)
    min_y = min(x[1] for x in m.keys())
    min_x = min(x[0] for x in m.keys())
    direction: Tuple[int, int] = (1, 0)
    points = [current]
    for i, instr in tqdm(enumerate(instructions), total=len(instructions), leave=False, desc="Following instructions"):
        # log(f"{'-'*10}{i:^5d}{'-'*10} {instr}")
        new_points, direction = _apply_instruction(instruction=instr, direction=direction, current=current, m=m)
        current = new_points[-1]
        points.extend(new_points)

    ret = 1000 * (current[1] - min_y + 1) + 4 * (current[0] - min_x + 1) + _conv_direction(direction=direction)[0]

    if draw:
        _draw_map(m=m, points=points, name="unfolded")

    return ret


@Task(year=2022, day=22, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    data: Tuple[_MAP_TYPE, _INSTR_LIST]
    m, instructions = data
    partners = _fold_cube(m=m)

    current = (11, 7)
    direction = (1, 0)
    log(_print_map(m=m, current=current, direction=direction))
    new_points, direction = _apply_instruction(instruction=1, current=current, direction=direction, m=m,
                                               partners=partners)
    current = new_points[-1]
    print(current, direction)
    log("-" * 15)
    log(_print_map(m=m, current=current, direction=direction))

    return 2


def _find_min_max(m: _MAP_TYPE) -> Tuple[Tuple[int, int], Tuple[int, int], int]:
    min_y, max_y = min(x[1] for x in m.keys()), max(x[1] for x in m.keys())
    min_x, max_x = min(x[0] for x in m.keys()), max(x[0] for x in m.keys())
    side_len = min(max_x - min_x + 1, max_y - min_y + 1) // 3
    return (min_x, max_x), (min_y, max_y), side_len


def _fold_cube(m: _MAP_TYPE) -> Dict[Tuple[int, int], _PARTNER_DICT]:
    (min_x, max_x), (min_y, max_y), side_len = _find_min_max(m=m)

    i = 1
    face_map: Dict[Tuple[int, int], int] = {}
    for y in range(min_y, max_y + 1, side_len):
        for x in range(min_x, max_x + 1, side_len):
            pt = (x, y)
            if pt in m:
                face_map[(x // side_len, (y // side_len))] = i
                i += 1
    partners = {}
    for face in face_map.keys():
        partners[face] = _find_partner(face=face, faces=set(face_map.keys()), side_len=side_len)
        print("-" * 15)

    return partners


def _find_partner(
        face: Tuple[int, int], faces: Set[Tuple[int, int]], side_len: int
) -> _PARTNER_DICT:
    ret: _PARTNER_DICT = {}
    # TOP BOTTOM
    for direction in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        t_direction = _tpl_apl(t1=_turn_direction(direction=direction, change="R"), f=int)
        if _tpl_add(face, direction) in faces:
            # print(f"{face} Has {direction} direct friend")
            ret[direction] = (lambda x: _tpl_add(t1=x, t2=direction), direction)
        elif _tpl_add(t1=_tpl_add(t1=face, t2=direction), t2=_tpl_mult(t_direction, 1)) in faces:
            # print(f"{face} Has {direction} {t_direction} friend")
            def _tmp(x: Tuple[int, int], _d: Tuple[int, int]) -> Tuple[int, int]:
                idx = _tpl_apl(_d, abs).index(1)  # 1
                idx_t = (idx + 1) % 2  # 0
                _r = [-1, -1]
                _rest = x[idx_t] % side_len
                _r[idx_t] = x[idx_t] + side_len - _rest
                _r[idx] = x[idx] - side_len + _rest
                return _r[0], _r[1]

            ret[direction] = _tmp, _tpl_mult(t_direction, 1)
        elif _tpl_add(t1=_tpl_add(t1=face, t2=direction), t2=_tpl_mult(t_direction, -1)) in faces:
            # print(f"{face} Has {direction} {_tpl_mult(t_direction, -1)} friend")
            def _tmp(x: Tuple[int, int], _d: Tuple[int, int]) -> Tuple[int, int]:
                idx = _tpl_apl(_d, abs).index(1)  # 1
                idx_t = (idx + 1) % 2  # 0
                _r = [-1, -1]
                _rest = x[idx_t] % side_len
                _r[idx_t] = x[idx_t] - _rest - 1
                _r[idx] = x[idx] - 1 - _rest
                return _r[0], _r[1]

            ret[direction] = _tmp, _tpl_mult(t_direction, -1)
        elif _tpl_add(t1=_tpl_add(t1=face, t2=direction), t2=_tpl_mult(t_direction, 2)) in faces:
            print(f"{face} Has {direction} {_tpl_mult(t_direction, 2)} friend")
            ret[direction] = 4
        elif _tpl_add(t1=_tpl_add(t1=face, t2=direction), t2=_tpl_mult(t_direction, -2)) in faces:
            print(f"{face} Has {direction} {_tpl_mult(t_direction, -2)} friend")
            ret[direction] = 5
        elif _tpl_add(t1=_tpl_add(t1=face, t2=_tpl_mult(t1=direction, f=-1)), t2=_tpl_mult(t_direction, 3)) in faces:
            print(f"{face} Has {direction} {_tpl_mult(t_direction, 3)} back friend")
            ret[direction] = 7
        elif _tpl_add(t1=_tpl_add(t1=face, t2=_tpl_mult(t1=direction, f=-1)), t2=_tpl_mult(t_direction, -3)) in faces:
            print(f"{face} Has {direction} {_tpl_mult(t_direction, -3)} back friend")
            ret[direction] = 7
        elif _tpl_add(t1=_tpl_add(t1=face, t2=_tpl_mult(t1=direction, f=-1)), t2=_tpl_mult(t_direction, 2)) in faces:
            print(f"{face} Has {direction} {_tpl_mult(t_direction, 2)} back friend")
            ret[direction] = 7
        elif _tpl_add(t1=_tpl_add(t1=face, t2=_tpl_mult(t1=direction, f=-1)), t2=_tpl_mult(t_direction, -2)) in faces:
            print(f"{face} Has {direction} {_tpl_mult(t_direction, -2)} back friend")
            ret[direction] = 7
        elif _tpl_add(t1=face, t2=_tpl_mult(t1=_turn_direction(_turn_direction(direction, "R"), "R"), f=3)) in faces:
            print(f"{face} Has {direction} mirrored friend")
            ret[direction] = 7
        elif _tpl_add(t1=face, t2=_tpl_add(_tpl_mult(t1=_turn_direction(_turn_direction(direction, "R"), "R"), f=3),
                                           _tpl_mult(t_direction, 1))) in faces:
            print(f"{face} Has {direction} mirrored {_tpl_mult(t_direction, 1)} friend")
            ret[direction] = 7
        elif _tpl_add(t1=face, t2=_tpl_add(_tpl_mult(t1=_turn_direction(_turn_direction(direction, "R"), "R"), f=3),
                                           _tpl_mult(t_direction, -1))) in faces:
            print(f"{face} Has {direction} mirrored {_tpl_mult(t_direction, -1)} friend")
            ret[direction] = 7
        elif _tpl_add(t1=face, t2=_tpl_add(_tpl_mult(t1=_turn_direction(_turn_direction(direction, "R"), "R"), f=3),
                                           _tpl_mult(t_direction, 2))) in faces:
            print(f"{face} Has {direction} mirrored {_tpl_mult(t_direction, 2)} friend")
            ret[direction] = 7
        elif _tpl_add(t1=face, t2=_tpl_add(_tpl_mult(t1=_turn_direction(_turn_direction(direction, "R"), "R"), f=3),
                                           _tpl_mult(t_direction, -2))) in faces:
            print(f"{face} Has {direction} mirrored {_tpl_mult(t_direction, -2)} friend")
            ret[direction] = 7
        else:
            raise Exception(f"{face} Has no {direction} friend")
            # print(f"{face} Has no {direction} friend")
            pass

    return ret


def _turn_direction(direction: Tuple[int, int], change: str) -> Tuple[int, int]:
    change = change.upper()
    return {
        (0, 1): {  # DOWN
            "R": (-1, 0),
            "L": (1, 0),
        },
        (0, -1): {  # UP
            "R": (1, 0),
            "L": (-1, 0),
        },
        (1, 0): {  # RIGHT
            "R": (0, 1),
            "L": (0, -1),
        },
        (-1, 0): {  # LEFT
            "R": (0, -1),
            "L": (0, 1),
        },
    }[direction][change.upper()]


def _conv_direction(direction: Tuple[int, int]) -> Tuple[int, str]:
    return {
        (0, 1): (1, "V"),
        (0, -1): (3, "^"),
        (1, 0): (0, ">"),
        (-1, 0): (2, "<"),
    }[direction]


def _tpl_add(t1: Tuple[int, int], t2: Tuple[int, int]) -> Tuple[int, int]:
    return t1[0] + t2[0], t1[1] + t2[1]


def _tpl_mult(t1: Tuple[int, int], f: int) -> Tuple[int, int]:
    return t1[0] * f, t1[1] * f


def _tpl_apl(t1: Tuple[int, int], f: Callable[[int], int]) -> Tuple[int, int]:
    return f(t1[0]), f(t1[1])


def _apply_instruction(
        instruction: _INSTRUCTION_TYPE, current: Tuple[int, int], direction: Tuple[int, int], m: _MAP_TYPE,
        partners: Dict[Tuple[int, int], _PARTNER_DICT] = None
) -> Tuple[List[Tuple[int, int]], Tuple[int, int]]:
    ret = [current]
    if isinstance(instruction, int):
        for _ in range(instruction):
            if partners is None:
                _next, _direction = _find_next(direction=direction, current=current, m=m)
            else:
                _next, _direction = _find_next_folded(direction=direction, current=current, m=m, partners=partners)
            if m[_next] is True:
                current = _next
                direction = _direction
                ret.append(current)
            else:
                break
    else:
        direction = _turn_direction(direction=direction, change=instruction)
    return ret, direction


def _find_next(
        direction: Tuple[int, int], current: Tuple[int, int], m: _MAP_TYPE,
) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    n = _tpl_add(t1=current, t2=direction)
    if n not in m:
        search_direction = _turn_direction(direction=_turn_direction(direction=direction, change="R"), change="R")
        _n = current
        while _n in m:
            _n = _tpl_add(t1=_n, t2=search_direction)
        _n = _tpl_add(t1=_n, t2=direction)
        if _n not in m:
            raise Exception()
        n = _n
    return n, direction


def _find_next_folded(
        direction: Tuple[int, int], current: Tuple[int, int], m: _MAP_TYPE,
        partners: Dict[Tuple[int, int], _PARTNER_DICT],
) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    n = _tpl_add(t1=current, t2=direction)

    if n not in m:
        (min_x, max_x), (min_y, max_y), side_len = _find_min_max(m=m)
        face = (current[0] // side_len, current[1] // side_len)
        partner_fun, _direction = partners[face][direction]
        n = partner_fun(current, direction)
        direction = _direction

    return n, direction


def _print_map(m: _MAP_TYPE, current: Tuple[int, int], direction: Tuple[int, int]) -> str:
    ret = []
    (min_x, max_x), (min_y, max_y), side_len = _find_min_max(m=m)

    for y in range(min_y, max_y + 1, 1):
        line = []
        for x in range(min_x, max_x + 1, 1):
            pt = (x, y)
            if current is not None and pt == current:
                if direction is not None:
                    line.append(_conv_direction(direction=direction)[1])
                else:
                    line.append("X")
            elif pt in m:
                line.append("." if m[pt] is True else "#")
            else:
                line.append(" ")
        ret.append(line)

    return "\n".join("".join(x) for x in ret)


def _draw_map(m: _MAP_TYPE, points: List[Tuple[int, int]], name: str):
    import os
    import matplotlib.pyplot as plt
    import numpy as np
    (min_x, max_x), (min_y, max_y), side_len = _find_min_max(m=m)
    _img = np.zeros((max_y - min_y + 1, max_x - min_x + 1), dtype=np.float)
    min_c, max_c = .1, 1
    for y in range(min_y, max_y + 1, 1):
        for x in range(min_x, max_x + 1, 1):
            pt = (x, y)
            if pt in m:
                _img[y, x] = max_c if m[pt] else min_c
    if len(points) > 0:
        rng = (max_c - min_c) / 2
        offset = .1 + ((max_c - min_c) - rng) / 2
        rng_step = rng / len(points)
        for i, (x, y) in enumerate(points):
            _img[y, x] = offset + i * rng_step
    fig, ax = plt.subplots()
    fig: plt.Figure
    ax: plt.Axes
    fig.set_size_inches(10, 12)
    fig.suptitle(name)
    ax.imshow(_img)
    ax.set_axis_off()
    fig.savefig(os.path.join(os.path.dirname(__file__), f"{name}.png"), dpi=600)
