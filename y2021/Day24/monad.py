from typing import List, Dict, Tuple
from copy import deepcopy
import queue

import numpy as np

from .alu import ALU, ALURegister


class MONAD:

    def __init__(self, alu_core: ALU, instruction_lines: List[str], number_len: int = 14):
        self._alu_core = alu_core
        self._instructions = [(x.split(" ")[0], tuple(x.split(" ")[1:])) for x in instruction_lines]
        self._number_len = number_len

    def find_valid_numbers(self) -> List[int]:
        from tqdm import tqdm

        states: Dict[ALURegister, int] = {self._alu_core.get_register(): 0}
        # states.put((np.zeros(4, dtype=int), []))

        with tqdm(self._instructions, desc=f"States: {len(states)}", leave=False) as pb:
            for op, data in pb:
                new_states: List[Tuple[ALURegister, int]] = []
                if op == "inp":
                    for register, model_num in states.items():
                        for i in range(1, 10):
                            new_register = register.__copy__()
                            self._alu_core.bind_input_memory(lambda: i)
                            self._alu_core.execute(op=op, register_vals=data, used_register=new_register)
                            new_states.append((new_register, model_num + 10 + i))
                else:
                    for register, model_num in states.items():
                        self._alu_core.execute(op=op, register_vals=data, used_register=register)
                        new_states.append((register, model_num))
                states.clear()
                for register, model_num in sorted(new_states, key=lambda x: x[1]):
                    states[register] = model_num
                pb.set_description(desc=f"States: {len(states)}")

        valid_model_numbers: List[int] = []
        while not states.empty():
            register, state = states.get()
            if self._alu_core.read_register(register="z", used_register=register) == 0:
                valid_model_numbers.append(int("".join(str(x) for x in state)))

        return sorted(valid_model_numbers)
