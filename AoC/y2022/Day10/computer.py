from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Generator, Callable, Any, Iterator

import numpy as np


class Instruction(ABC):

    @classmethod
    def inst_name(cls) -> str:
        return cls.__name__.lower()

    @abstractmethod
    def execute(self, register: np.ndarray, *args) -> Generator[np.ndarray, np.ndarray, int]:
        pass


class Computer:

    def __init__(self, instructions: Dict[str, Instruction], register_size: int = 1, register_type=int, initial_register = 1):
        self._instructions = instructions
        self._register_size = register_size
        self._register_type = register_type
        self._initial_register = initial_register
        self._register = np.zeros(register_size, dtype=register_type)
        self._register[:] = initial_register

    def run_code(self, code: List[Tuple[str, Tuple[Any, ...]]], global_register: bool = False,
                 callback: Callable[[int, np.ndarray], bool] = None) -> Tuple[int, np.ndarray]:
        if global_register:
            register = self._register
        else:
            register = np.zeros(self._register_size, dtype=self._register_type)
            register[:] = self._initial_register
        if callback is None:
            def callback(*_):
                pass
        cycle = 1
        for instruction, args in code:
            for _ in self._instructions[instruction].execute(register, *args):
                if not callback(cycle, register):
                    break
                cycle += 1
        callback(cycle, register)
        return cycle, register.copy()

    def __str__(self):
        return f"Computer with {self._register_size} registers and {len(self._instructions)} instructions"


class NOOP(Instruction):
    def execute(self, register: np.ndarray, *args) -> Iterator[np.ndarray]:
        yield register


class ADDX(Instruction):
    def execute(self, register: np.ndarray, *args) -> Iterator[int]:
        if len(args) != 1:
            raise Exception()
        value = int(args[0])
        yield register
        yield register
        register[0] += value


INSTRUCTIONS = {
    NOOP.inst_name(): NOOP(),
    ADDX.inst_name(): ADDX(),
}
