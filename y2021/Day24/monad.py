from typing import List, Dict, Tuple, Iterable
from copy import deepcopy
import queue

import numpy as np

from .alu import ALU, ALUInstructionList, ALUInstruction, Inp


class MONAD:

    def __init__(self, instruction_lines: List[str], number_len: int = 14):
        self._instructions = ALUInstructionList(*instruction_lines)
        self._number_len = number_len
        c = 0
        for instruction in self._instructions:
            if instruction.operation_isinstance(Inp):
                c += 1
        if c != self._number_len:
            raise ValueError(f"The amount of inputs in your instructions dont match the wanted length of model number. "
                             f"{c} != {self._number_len}")

    def force_biggest_number(self):
        from tqdm import tqdm

        def iter_numbs(_number_len: int) -> Iterable[List[int]]:
            if _number_len <= 0:
                yield []
            else:
                for i in range(9, 0, -1):
                    j = [i]
                    for other in iter_numbs(_number_len=_number_len - 1):
                        yield j + other

        with tqdm(desc=f"Iterating potential numbers", leave=False, total=9**14) as pb:
            for x in iter_numbs(_number_len=self._number_len):

                pb.update()

    def find_valid_numbers(self) -> List[int]:
        from tqdm import tqdm

        states: Dict[int, Tuple[np.ndarray, List[int]]] = {
            0: (np.zeros(self._instructions.get_suggested_register_size(), dtype=int), [0])
        }
        # states.put((np.zeros(4, dtype=int), []))

        iterative_memory = [0]

        def memory() -> int:
            ret = iterative_memory[0] + 1
            iterative_memory[0] = (iterative_memory[0] + 1) % 10
            return ret

        self._instructions.get_alu_core().bind_input_memory(memory_retriever=memory)

        # print("\n".join(str(x) for x in self._instructions))
        # print(", ".join(f"{k}: {self._instructions.get_register_idx(k)}" for k in ["w", "x", "y", "z"]))
        # exit()

        with tqdm(desc=f"States: {len(states)}", leave=False, total=len(self._instructions)) as pb:
            for instruction in self._instructions:
                pb.update()
                instruction: ALUInstruction
                new_states: Dict[int, Tuple[np.ndarray, List[int]]] = {}
                if instruction.operation_isinstance(Inp):
                    for register, model_num in states.values():
                        for i in range(1, 10):
                            new_register = register.copy()
                            # self._alu_core.bind_input_memory(lambda: i)
                            instruction(new_register)
                            new_nums = []
                            for num in model_num:
                                new_nums.append(num * 10 + i)
                            h = hash(new_register.tostring())
                            if h not in new_states:
                                new_states[h] = (new_register, [])
                            new_states[h][1].extend(new_nums)
                else:
                    for register, model_num in states.values():
                        instruction(register)
                        h = hash(register.tostring())
                        if h not in new_states:
                            new_states[h] = (register, [])
                        new_states[h][1].append(model_num)
                states = new_states

        valid_model_numbers: List[int] = []
        z_id = self._instructions.get_register_idx("z")
        for register, model_num in states.values():
            register: np.ndarray
            if register[z_id] == 0:
                valid_model_numbers.extend(model_num)

        self._instructions.get_alu_core().reset()

        return sorted(valid_model_numbers)
