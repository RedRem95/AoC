from typing import Callable, AnyStr, Tuple, List, Any

import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022, day=10)
def preproc_1(data):
    ret = []
    for line in data:
        line = line.strip()
        if len(line) <= 0:
            continue
        instruction, *args = line.split(" ")
        ret.append((instruction, args))
    return ret


@Task(year=2022, day=10, task=1)
def task01(data: List[Tuple[str, Tuple[Any, ...]]], log: Callable[[AnyStr], None]):
    from .computer import Computer, INSTRUCTIONS
    comp = Computer(instructions=INSTRUCTIONS, register_size=1, register_type=int)
    log(f"Executing {comp} with {len(data)} commands")
    ret = [0]

    def callback(cycle: int, register: np.ndarray) -> bool:
        if (cycle - 20) % 40 == 0:
            ret[0] += cycle * register[0]
        return True
    cycles, final_register = comp.run_code(code=data, global_register=False, callback=callback)
    log(f"Ran program. Took {cycles} cycles. Final register is {final_register}")
    return ret[0]


@Task(year=2022, day=10, task=2, extra_config={"crt_size": (40, 6)})
def task02(data, log: Callable[[AnyStr], None], crt_size: Tuple[int, int]):
    from .crt import CRT
    from .computer import Computer, INSTRUCTIONS
    crt = CRT(*crt_size, pixel_type=bool, pixel={True: "█", False: " "})
    comp = Computer(instructions=INSTRUCTIONS, register_size=1, register_type=int)
    log(f"Drawing on {crt} powered by a {comp}")
    comp.run_code(code=data, global_register=False, callback=crt.draw_computer)
    log(f"Final screen after {len(data)} instructions")
    log(crt.print_screen(draw_header=True, draw_box=True))
    return "See logs"
