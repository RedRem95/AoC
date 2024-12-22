import os.path
from typing import Callable, AnyStr, Generator

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor

from .program import adv, bdv, cdv, jnz, bxc, out, bst, bxl, replace_in_tpl

if os.path.basename(os.path.dirname(os.path.dirname(__file__))).startswith("y"):
    _YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[len("y"):])
else:
    raise Exception()

if os.path.basename(os.path.dirname(__file__)).startswith("Day"):
    _DAY = int(os.path.basename(os.path.dirname(__file__))[len("Day"):])
else:
    raise Exception()

op_codes = {
    0: adv,
    1: bxl,
    2: bst,
    3: jnz,
    4: bxc,
    5: out,
    6: bdv,
    7: cdv,
}


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    register, operators = {}, []
    for line in (x for x in data if len(x) > 0):
        if line.startswith("Register"):
            register[line[len("Register ")][0]] = int(line.split(":")[-1].strip())
        if line.startswith("Program"):
            operators.extend([int(x) for x in line.split(":")[-1].strip().split(",") if len(x) > 0])
    return tuple(v for k, v in sorted(register.items())), operators


def run_program(register, operators) -> Generator[int, int, None]:
    idx = 0
    while idx + 1 < len(operators):
        op_code = op_codes[operators[idx]]
        register, idx, tmp_out = op_code(idx, operators[idx + 1], register)
        if tmp_out is not None:
            yield tmp_out


@Task(year=2024, day=_DAY, task=1)
def task01(data, log: Callable[[AnyStr], None]):
    outs = list(run_program(*data))
    return ",".join(str(x) for x in outs)


@Task(year=2024, day=_DAY, task=2)
def task02_symbolic(data, log: Callable[[AnyStr], None]):
    from sympy import Symbol, Eq, solve
    a = Symbol("A", positive=True, integer=True)
    register, operators = data
    register = replace_in_tpl(tpl=register, val=a, idx=0)
    outs = []
    for dis_out in run_program(register=register, operators=operators):
        outs.append(dis_out)
        if len(outs) == len(operators):
            break
    eqs = [Eq(eq, v) for eq, v in zip(outs, operators)]
    e = eqs[0]
    print("\n".join(str(o) for o in eqs))
    print(solve(eqs, a, dict=True))
    return None


# @Task(year=2024, day=_DAY, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    from tqdm import tqdm
    register, operators = data
    target_i = len(operators)
    a = 0
    with tqdm(desc="Testing registers", leave=False) as pbar:
        while True:
            still_searching = False
            register = replace_in_tpl(tpl=register, val=a, idx=0)
            for i, op in enumerate(run_program(register=register, operators=operators)):
                if i >= target_i or op != operators[i]:
                    still_searching = True
                    break
            still_searching = still_searching or i + 1 != target_i
            if not still_searching:
                break
            a += 1
            pbar.update(1)
    return a
