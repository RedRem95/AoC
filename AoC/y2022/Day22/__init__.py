import itertools
import math
from typing import Callable, AnyStr, Dict, Tuple, Union, List, Iterator, Optional

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor
from tqdm import tqdm

_MAP_TYPE = Dict[Tuple[int, int], bool]
_INSTRUCTION_TYPE = Union[str, int]
_INSTR_LIST = List[_INSTRUCTION_TYPE]
_PARTNER_TYPE = Dict[Tuple[Tuple[int, int], Tuple[int, int]], Tuple[Tuple[int, int], Tuple[int, int]]]


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


@Task(year=2022, day=22, task=1, extra_config={"draw": False})
def task01(data, log: Callable[[AnyStr], None], draw: bool, start_pos=None, start_direction=None):
    data: Tuple[_MAP_TYPE, _INSTR_LIST]
    m, instructions = data
    log(f"Using map in unfolded mode")
    ret = _run(
        m=m, instr=instructions, partner_fun=_partners_unfolded, return_fun=_calc_default_ret, log=log,
        file_name="unfolded" if draw else None, start_pos=start_pos, start_direction=start_direction,
    )
    return ret


@Task(year=2022, day=22, task=2, extra_config={"draw": False})
def task02(data, log: Callable[[AnyStr], None], draw: bool, start_pos=None, start_direction=None):
    data: Tuple[_MAP_TYPE, _INSTR_LIST]
    m, instructions = data
    log(f"Using map in folded mode")
    ret = _run(
        m=m, instr=instructions, partner_fun=_partners_folded, return_fun=_calc_default_ret, log=log,
        file_name="folded" if draw else None, start_pos=start_pos, start_direction=start_direction,
    )
    return ret


def _find_default_start(m: _MAP_TYPE) -> Tuple[int, int]:
    min_y = min(x[1] for x in m.keys() if any(m[y] is True for y in m.keys() if y[1] == x[1]))
    min_x = min(x[0] for x in m.keys() if x[1] == min_y and m[x] is True)
    return min_x, min_y


def _calc_default_ret(m: _MAP_TYPE, pt: Tuple[int, int], direction: Tuple[int, int]) -> int:
    (min_x, max_x), (min_y, max_y) = _find_min_max(m=m)
    return 1000 * (pt[1] - min_y + 1) + 4 * (pt[0] - min_x + 1) + _conv_direction(direction=direction)[0]


def _run(
        m: _MAP_TYPE, instr: _INSTR_LIST, log: Callable[[AnyStr], None],
        partner_fun: Callable[[_MAP_TYPE], _PARTNER_TYPE],
        return_fun: Callable[[_MAP_TYPE, Tuple[int, int], Tuple[int, int]], int], file_name: Optional[str] = None,
        start_pos: Optional[Tuple[int, int]] = None, start_direction: Optional[Tuple[int, int]] = None,
) -> int:
    if start_pos is None:
        start_pos = _find_default_start(m=m)
    if start_direction is None:
        start_direction = (1, 0)
    partners = partner_fun(m)
    current = start_pos
    direction = start_direction
    log(f"Running {len(instr)} instructions")
    log(f"Starting at {current} facing {_conv_direction(direction=direction)[2].lower()}")
    points: List[Tuple[int, int]] = [current]
    for i, instr in tqdm(enumerate(instr), total=len(instr), leave=False, desc="Following instructions"):
        # log(f"{'-'*10}{i:^5d}{'-'*10} {instr}")
        new_points, direction = _apply_instruction(instruction=instr, direction=direction, current=current, m=m,
                                                   partners=partners)
        current = new_points[-1]
        points.extend(new_points)

    ret = return_fun(m, current, direction)
    log(f"After {len(points)} steps you are at {current} facing {_conv_direction(direction=direction)[2].lower()}")
    if file_name is not None:
        _draw_map(m=m, points=points, name=file_name)
    return ret


def _find_outline(m: _MAP_TYPE) -> Iterator[Tuple[Tuple[int, int], Tuple[int, int]]]:
    direction = (1, 0)
    start_y = min(y for x, y in m.keys())
    start_x = min(x for x, y in m.keys() if y == start_y)
    start_pos = (start_x, start_y)
    current_pos = start_pos
    yield direction, current_pos
    while True:
        n1 = _tpl_add(current_pos, direction)
        n2 = _tpl_add(n1, _turn_direction(direction, "L"))
        if n2 in m:
            current_pos = n2
            direction = _turn_direction(direction, "L")
        elif n1 not in m:
            current_pos = current_pos
            direction = _turn_direction(direction, "R")
        else:
            current_pos = n1
            direction = direction
        yield direction, current_pos
        if current_pos == start_pos:
            break


def _find_edges(m: _MAP_TYPE) -> Iterator[Tuple[Tuple[int, int], List[Tuple[int, int]]]]:
    outline = _find_outline(m=m)
    pre_edges = itertools.groupby(outline, key=lambda x: x[0])
    pre_edges = [(k, [_v[1] for _v in v]) for k, v in pre_edges]
    side_length = math.gcd(*[len(e) for _, e in pre_edges])

    for d, edge in pre_edges:
        for i in range(0, len(edge), side_length):
            yield d, edge[i:i + side_length]


def _partners_unfolded(m: _MAP_TYPE) -> _PARTNER_TYPE:
    edges = list(_find_edges(m=m))
    ret: _PARTNER_TYPE = {}
    for d, edge in edges:
        for pt in edge:
            off_dir = _turn_direction(direction=d, change="L")
            on_dir = _turn_direction(direction=d, change="R")
            n = pt
            while _tpl_add(n, on_dir) in m:
                n = _tpl_add(n, on_dir)
            ret[(off_dir, pt)] = (off_dir, n)
    return ret


def _partners_folded(m: _MAP_TYPE) -> _PARTNER_TYPE:
    edges = [(direction, (edges, direction)) for direction, edges in _find_edges(m=m)]
    ret: _PARTNER_TYPE = {}
    pairs = []
    while len(edges) > 0:
        i = 0
        while i < len(edges) - 1:
            direction1, edge1 = edges[i]
            direction2, edge2 = edges[i + 1]
            if direction2 == _turn_direction(direction1, "L"):
                pairs.append(((direction1, edge1), (direction2, edge2)))
                edges[i:i + 2] = []
                edges[i:] = [(_turn_direction(d, "L"), e) for d, e in edges[i:]]
            else:
                i += 1
    for (direction1, edge1), (direction2, edge2) in pairs:
        edge_list1, orig_direction1 = edge1
        edge_list2, orig_direction2 = edge2
        on1, off1 = _turn_direction(orig_direction1, "R"), _turn_direction(orig_direction1, "L")
        on2, off2 = _turn_direction(orig_direction2, "R"), _turn_direction(orig_direction2, "L")
        for pt1, pt2 in zip(edge_list1, edge_list2[::-1]):
            ret[(off1, pt1)] = (on2, pt2)
            ret[(off2, pt2)] = (on1, pt1)
    return ret


def _find_min_max(m: _MAP_TYPE) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    min_y, max_y = min(x[1] for x in m.keys()), max(x[1] for x in m.keys())
    min_x, max_x = min(x[0] for x in m.keys()), max(x[0] for x in m.keys())
    return (min_x, max_x), (min_y, max_y)


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


def _conv_direction(direction: Tuple[int, int]) -> Tuple[int, str, str]:
    return {
        (0, 1): (1, "V", "Down"),
        (0, -1): (3, "^", "Up"),
        (1, 0): (0, ">", "Right"),
        (-1, 0): (2, "<", "Left"),
    }[direction]


def _tpl_add(t1: Tuple[int, int], t2: Tuple[int, int]) -> Tuple[int, int]:
    return t1[0] + t2[0], t1[1] + t2[1]


def _tpl_mult(t1: Tuple[int, int], f: int) -> Tuple[int, int]:
    return t1[0] * f, t1[1] * f


def _tpl_apl(t1: Tuple[int, int], f: Callable[[int], int]) -> Tuple[int, int]:
    return f(t1[0]), f(t1[1])


def _apply_instruction(
        instruction: _INSTRUCTION_TYPE, current: Tuple[int, int], direction: Tuple[int, int], m: _MAP_TYPE,
        partners: _PARTNER_TYPE
) -> Tuple[List[Tuple[int, int]], Tuple[int, int]]:
    ret = [current]
    if isinstance(instruction, int):
        for _ in range(instruction):
            _direction, _next = partners.get((direction, current), (direction, _tpl_add(current, direction)))
            if _next not in m:
                raise Exception()
            if m[_next] is True:
                current = _next
                direction = _direction
                ret.append(current)
            else:
                break
    else:
        direction = _turn_direction(direction=direction, change=instruction)
    return ret, direction


def _print_map(m: _MAP_TYPE, current: Tuple[int, int], direction: Tuple[int, int]) -> str:
    ret = []
    (min_x, max_x), (min_y, max_y) = _find_min_max(m=m)

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
    (min_x, max_x), (min_y, max_y) = _find_min_max(m=m)
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


def _sign(x):
    return 1 if x >= 0 else -1
