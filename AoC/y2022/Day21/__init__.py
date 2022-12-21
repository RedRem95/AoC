from typing import Callable, AnyStr, Dict

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor

from .monkey import Monkey, MathMonkey, HumanMonkey, EqualMonkey


@Preprocessor(year=2022, day=21)
def preproc_1(data):
    horde = Monkey.parse_horde(data=[x.strip() for x in data if len(x.strip()) > 0])
    return horde


@Task(year=2022, day=21, task=1, extra_config={"root_key": "root"})
def task01(data: Dict[str, Monkey], log: Callable[[AnyStr], None], root_key: str):
    log(f"Horde has {len(data)} monkeys")
    log(f"Listening for monkey {root_key}")
    ret = int(data["root"].get_value())
    log(f"{root_key} screams {ret}")
    return ret


@Task(year=2022, day=21, task=2, extra_config={"human_key": "humn", "root_key": "root"})
def task02(data: Dict[str, Monkey], log: Callable[[AnyStr], None], human_key: str, root_key: str):
    log(f"Horde has {len(data)} monkeys")
    log(f"Swapping {root_key} for a {EqualMonkey.__name__} and {human_key} for a {HumanMonkey.__name__}")
    if isinstance(data[root_key], MathMonkey):
        # noinspection PyUnresolvedReferences
        data[root_key] = EqualMonkey(monkey1=data[root_key].monkey1, monkey2=data[root_key].monkey2, horde=data)
    else:
        raise Exception()
    me = HumanMonkey(value=0)
    data[human_key] = me

    log(f"Solving monkey-calculation so you know what to scream")
    solve = int(HumanMonkey.solve(horde=data))
    if not data["root"].get_value() is True:
        return None
    log(f"You need to scream {solve}")

    return solve
