from typing import Dict, Callable, Tuple, Union, Iterator, List, Type
from abc import ABC, abstractmethod
import math
from enum import Enum

import numpy as np


class ALU:

    def __init__(self):
        self._input_operation = Inp()
        self._operations: Dict[str, ALUOperation] = {}
        self.register_fun(self._input_operation)
        self.register_fun(Add())
        self.register_fun(Mul())
        self.register_fun(Div())
        self.register_fun(Mod())
        self.register_fun(Eql())

    def __getitem__(self, item: str) -> "ALUOperation":
        return self._operations[item]

    def bind_input_memory(self, memory_retriever: Callable[[], int]):
        self._input_operation.bind_memory(memory_retriever=memory_retriever)

    def register_fun(self, operation: "ALUOperation", name: str = None):
        if name is None:
            name = operation.__class__.__name__.lower()
        if name == "inp" and name in self._operations:
            raise KeyError(f"You can only bind the input operation once")
        self._operations[name] = operation

    def reset(self):
        for fun in self._operations.values():
            fun.reset()


class ValueType(Enum):
    Constant = 1
    Register = 2


class ALUInstructionList:
    def __init__(self, *instructions: str, alu_core: ALU = None):
        if alu_core is None:
            alu_core = ALU()
        self._alu_core = alu_core
        self._instructions: List[ALUInstruction] = []
        self._register_mapping: Dict[str, int] = {}

        def _is_int(_x: str) -> bool:
            try:
                int(_x)
                return True
            except ValueError:
                return False

        for inst in instructions:
            op, *data = inst.split(" ")
            operation = self._alu_core[op.strip()]
            data_conv: List[Tuple[int, ValueType]] = []
            for d in data:
                d: str
                if _is_int(d):
                    data_conv.append((int(d), ValueType.Constant))
                else:
                    if d not in self._register_mapping:
                        self._register_mapping[d] = len(self._register_mapping)
                    data_conv.append((self._register_mapping[d], ValueType.Register))
            self._instructions.append(ALUInstruction(op=operation, data=data_conv))

    def get_register_idx(self, key: str) -> int:
        return self._register_mapping[key]

    def get_suggested_register_size(self) -> int:
        return len(self._register_mapping)

    def get_alu_core(self) -> ALU:
        return self._alu_core

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __len__(self):
        return len(self._instructions)

    def __getitem__(self, item):
        return self._instructions[item]


class ALUInstruction:

    def __init__(self, op: "ALUOperation", data: List[Tuple[int, ValueType]]):
        if len(data)< 1:
            raise Exception("You cant execute an instruction without data")
        if data[0][1] != ValueType.Register:
            raise Exception("The first instruction parameter cant be a constant value. The result will be stored here")
        self._op = op
        self._data = data

    def forward(self, register: np.ndarray) -> np.ndarray:
        res = self._op(*[register[x] if t == ValueType.Register else x for x, t in self._data])
        register[self._data[0][0]] = res
        return register

    def __call__(self, register: np.ndarray) -> np.ndarray:
        return self.forward(register=register)

    def operation_isinstance(self, typ: Type):
        return isinstance(self._op, typ)

    def __str__(self):
        return f"{self._op.__class__.__name__.lower()}({', '.join(f'r({i})' if t == ValueType.Register else str(i) for i, t in self._data)})"


class ALUOperation(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def forward(self, *values: int) -> int:
        pass

    def __call__(self, *args):
        return self.forward(*args)

    def reset(self):
        pass


class Add(ALUOperation):
    def forward(self, *values: int) -> int:
        return int(sum(values))


class Mul(ALUOperation):
    def forward(self, *values: int) -> int:
        return int(math.prod(values))


class Div(ALUOperation):
    def forward(self, *values: int) -> int:
        if len(values) != 2:
            raise Exception(f"You can only divide 2 values. {len(values)} given")
        return values[0] // values[1]


class Mod(ALUOperation):
    def forward(self, *values: int) -> int:
        if len(values) != 2:
            raise Exception(f"You can only take modulo 2 values. {len(values)} given")
        return values[0] % values[1]


class Eql(ALUOperation):
    def forward(self, *values: int) -> int:
        if len(values) <= 1:
            return True
        return int(all(x == values[0] for x in values[1:]))


class Inp(ALUOperation):
    def __init__(self):
        super().__init__()
        self._memory_retrieve: Callable[[], int] = lambda: 0

    def forward(self, *values: int) -> int:
        return self._memory_retrieve()

    def bind_memory(self, memory_retriever: Callable[[ALU], int]):
        self._memory_retrieve = memory_retriever

    def reset(self):
        self._memory_retrieve = lambda: 0
