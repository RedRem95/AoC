import os.path
from typing import Callable, AnyStr, List, Tuple, Dict

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor

if os.path.basename(os.path.dirname(__file__)).startswith("Day"):
    _DAY = int(os.path.basename(os.path.dirname(__file__))[len("Day"):])
else:
    raise Exception()

_BUTTONS = {
    "A": 3,
    "B": 1
}


def solve_lin_alg(A, b):
    n = len(A)
    augmented_matrix = [A[i] + [b[i]] for i in range(n)]

    for i in range(n):
        max_row = max(range(i, n), key=lambda r: abs(augmented_matrix[r][i]))

        if i != max_row:
            augmented_matrix[i], augmented_matrix[max_row] = augmented_matrix[max_row], augmented_matrix[i]

        pivot = augmented_matrix[i][i]
        if abs(pivot) < 1e-10:
            raise ValueError("No solution")

        augmented_matrix[i] = [x / pivot for x in augmented_matrix[i]]

        for j in range(n):
            if j != i:
                factor = augmented_matrix[j][i]
                augmented_matrix[j] = [augmented_matrix[j][k] - factor * augmented_matrix[i][k] for k in range(n + 1)]
    return [augmented_matrix[i][-1] for i in range(n)]


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    ret = [{}]
    for line in (x.strip() for x in data):
        if len(line) <= 0:
            ret.append({})
            continue
        if line.startswith("Button "):
            btn_id = line[len("Button:"):][0]
            x = int(line.split(",")[0].split("+")[1])
            y = int(line.split(",")[1].split("+")[1])
            ret[-1][btn_id] = (x, y)
        elif line.startswith("Prize:"):
            x = int(line.split(",")[0].split("=")[1])
            y = int(line.split(",")[1].split("=")[1])
            ret[-1]["_"] = (x, y)
    return [x for x in ret if len(x) > 0]


def optimize_machine(machine: Dict[str, Tuple[int, int]]):
    target = [x for x in machine["_"]]
    buttons = list(_BUTTONS.keys())

    c = [_BUTTONS[k] for k in buttons]
    A = [[machine[x][i] for x in buttons] for i in range(len(target))]

    try:
        r = solve_lin_alg(A=A, b=target)
        eps = 0.0001
        r_int = [round(x) for x in r]
        if all(xr - eps <= x <= xr + eps and x >= 0 for x, xr in zip(r, r_int)):
            ret = sum([int(x) * int(y) for x, y in zip(c, r_int)])
            return ret
        raise ValueError()
    except ValueError:
        return None


def run(data: List[Dict[str, Tuple[int, int]]], log: Callable[[AnyStr], None]) -> int:
    log(f"Trying to solve {len(data)} machines, "
        f"where {' and '.join(f'a press on {b} costs {c}' for b, c in _BUTTONS.items())}")
    ret = [optimize_machine(x) for x in data]
    ret = [x for x in ret if x is not None]
    log(f"{len(ret)} machines are solvable. That are {len(ret) / len(data) * 100:.2f}% of the machines")
    ret = sum(0 if x is None else x for x in ret)
    log(f"In sum you will need {ret} tokens to win all winnable prices")
    return ret


@Task(year=2024, day=_DAY, task=1)
def task01(data, log: Callable[[AnyStr], None]):
    return run(data=data, log=log)


@Task(year=2024, day=_DAY, task=2, extra_config={"adjust_value": 10000000000000})
def task02(data, log: Callable[[AnyStr], None], adjust_value: int):
    log(f"Adjusting price positions by {adjust_value}")
    data_adjust = []
    for d in data:
        d["_"] = tuple(x + adjust_value for x in d["_"])
        data_adjust.append(d)
    return run(data=data_adjust, log=log)
