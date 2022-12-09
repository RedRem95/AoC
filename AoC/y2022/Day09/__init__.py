from typing import Callable, AnyStr, List, Tuple
import os

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022, day=9)
def preproc_1(data):
    ret = []
    for line in data:
        line = line.strip()
        if len(line) <= 0:
            continue
        direction, count = line.split(" ")
        ret.append((direction, int(count)))
    return ret


@Task(year=2022, day=9, task=1, extra_config={"draw": False})
def task01(data: List[Tuple[str, int]], log: Callable[[AnyStr], None], draw: bool):
    simmed = _sim(sim_data=data, log=log, knot_count=1)
    if draw:
        fig, _ = _draw(traversed=simmed)
        fig.savefig(os.path.join(os.path.dirname(__file__), f"{1} knot.png"), dpi=600)
    return len(set(simmed[-1]))


@Task(year=2022, day=9, task=2, extra_config={"knot_count": 9, "draw": False})
def task02(data, log: Callable[[AnyStr], None], draw: bool, knot_count: int):
    simmed = _sim(sim_data=data, log=log, knot_count=knot_count)
    if draw:
        fig, _ = _draw(traversed=simmed)
        fig.savefig(os.path.join(os.path.dirname(__file__), f"{knot_count} knots.png"), dpi=600)
    return len(set(simmed[-1]))


def _draw(traversed: List[List[Tuple[int, int]]]):
    import matplotlib.pyplot as plt
    cols = int(np.ceil(np.sqrt(len(traversed))))
    rows = int(np.ceil(len(traversed) / cols))
    fig, _ax = plt.subplots(nrows=rows, ncols=cols)
    ax_list = list(np.array([_ax]).ravel())
    fig: plt.Figure
    ax_list: List[plt.Axes]

    for ax in ax_list:
        ax.axis("off")

    fig.set_size_inches(w=cols * 5, h=0.2 + rows * 5)
    fig.suptitle(f"Travels of head and {len(traversed) - 1} knots")

    for i, t in enumerate(traversed):
        ax = ax_list[i]
        ax.set_title('head' if i == 0 else f'{i}. knot' if i < len(traversed) - 1 else 'tail')
        x, y = [_[0] for _ in t], [_[1] for _ in t]
        min_x, max_x, min_y, max_y = min(x), max(x), min(y), max(y)
        diff_x, diff_y = max_x - min_x, max_y - min_y

        if diff_x > diff_y:
            im_size = diff_x
            x_off = -min_x
            y_off = -min_y + (diff_x - diff_y) // 2
        else:
            im_size = diff_y
            y_off = -min_y
            x_off = -min_x + (diff_y - diff_x) // 2

        t = [_add(x, (x_off, y_off)) for x in t]
        im = np.zeros((im_size+1, im_size+1), dtype=bool)
        for trav in t:
            im[trav[0], trav[1]] = 1
        ax.imshow(im, aspect="equal", interpolation=None)

    return fig, ax_list

def _sim(sim_data: List[Tuple[str, int]], log: Callable[[str], None], knot_count: int) -> List[List[Tuple[int, int]]]:
    if knot_count < 0:
        raise ValueError(f"You cant simulate a rope with less than 0 knots")
    log(f"Simulating a rope with {knot_count} knot{'s' if knot_count != 1 else ''} for {len(sim_data)} steps")
    direction_data = {
        "L": (-1, 0),
        "R": (1, 0),
        "U": (0, 1),
        "D": (0, -1),
    }

    traversed: List[List[Tuple[int, int]]] = [[] for _ in range(knot_count + 1)]
    head, tail = (0, 0), [(0, 0) for _ in range(knot_count)]

    for direction, count in sim_data:
        for _ in range(count):
            head = _add(head, direction_data[direction])
            traversed[0].append(head)
            cur_tail = head
            for i in range(knot_count):
                tail[i] = _move_tail(head=cur_tail, tail=tail[i])
                cur_tail = tail[i]
                traversed[i+1].append(cur_tail)

    log(f"After {len(sim_data)} steps the")
    for i, sub_traversed in enumerate(traversed):
        log(f"{'head' if i == 0 else f'{i}. knot' if i < len(traversed) - 1 else 'tail':>10s} traversed "
            f"{len(sub_traversed)} steps ({len(set(sub_traversed))} unique)")

    return traversed


def _add(t1: Tuple[int, int], t2: Tuple[int, int]) -> Tuple[int, int]:
    return t1[0] + t2[0], t1[1] + t2[1]


def _diff(t1: Tuple[int, int], t2: Tuple[int, int]) -> Tuple[int, int]:
    return t1[0] - t2[0], t1[1] - t2[1]


def _abs(t1: Tuple[int, int]) -> Tuple[int, int]:
    return abs(t1[0]), abs(t1[1])


def _move_tail(head: Tuple[int, int], tail: Tuple[int, int]) -> Tuple[int, int]:
    diff = _diff(t1=head, t2=tail)
    abs_diff = _abs(diff)
    if max(abs_diff) <= 1:
        return tail
    return _add(t1=tail, t2=(int(np.sign(diff[0])), int(np.sign(diff[1]))))
