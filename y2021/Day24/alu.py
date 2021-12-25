from typing import Dict, Callable, Tuple, Union, Iterator
from abc import ABC, abstractmethod
import math

import numpy as np


class ALU:

    _COUNTER: int = 0

    def __init__(self, *register_ids: str):
        self._id = self.__class__._COUNTER
        self.__class__._COUNTER += 1

        self._default_register = ALURegister(*register_ids)

        self._input_operation = Inp()
        self._operations: Dict[str, ALUOperation] = {}
        self.register_fun(self._input_operation)
        self.register_fun(Add())
        self.register_fun(Mul())
        self.register_fun(Div())
        self.register_fun(Mod())
        self.register_fun(Eql())

    def execute(self, op: str, register_vals: Tuple[Union[str, int], ...], used_register: "ALURegister" = None):
        if used_register is None:
            used_register = self._default_register
        operation = self._operations[op]
        values = tuple(used_register[x] for x in register_vals)
        result = operation(*values)
        used_register[register_vals[0]] = result

    def read_register(self, register: str, used_register: np.ndarray = None):
        if used_register is None:
            used_register = self._default_register
        return used_register[register]

    def bind_input_memory(self, memory_retriever: Callable[["ALU"], int]):
        self._input_operation.bind_memory(memory_retriever=memory_retriever)

    def register_fun(self, operation: "ALUOperation", name: str = None):
        if name is None:
            name = operation.__class__.__name__.lower()
        if name == "inp" and name in self._operations:
            raise KeyError(f"You can only bind the input operation once")
        self._operations[name] = operation

    def reset(self):
        for op in self._operations.values():
            op.reset()
        self._default_register.reset()

    def get_register(self):
        return self._default_register

    def __str__(self, used_register: np.ndarray = None):
        if used_register is None:
            used_register = self._default_register
        return f"ALU<{len(self._operations)} ops; {', '.join(f'{k}: {v}' for k, v in used_register)}>"

    def __copy__(self):
        ret = ALU()
        ret._default_register = self._default_register.__copy__()
        return ret

    def __hash__(self):
        return self._id


class ALURegister:
    def __init__(self, *register_ids: str):
        for register_id in register_ids:
            try:
                float(register_id)
                raise ValueError(f"Cant use a Numeric value for ALU-Register. Found {register_id}")
            except ValueError:
                pass

        self._register_id_to_id: Dict[str, int] = {x: i for i, x in enumerate(register_ids)}
        self._register: np.ndarray = np.zeros(len(register_ids), dtype=int)

    def __getitem__(self, item: Union[int, str]) -> int:
        if item in self._register_id_to_id:
            return self._register[self._register_id_to_id[item]]
        return int(item)

    def __setitem__(self, key: str, value: int):
        if key in self._register_id_to_id:
            self._register[self._register_id_to_id[key]] = value

    def __copy__(self):
        ret = ALURegister(*[x for x, y in sorted(self._register_id_to_id.items(), key=lambda x: x[1])])
        ret._register = self._register.copy()
        return ret

    def __iter__(self) -> Iterator[Tuple[str, int]]:
        for k, v in self._register_id_to_id.items():
            yield k, self._register[v]

    def __hash__(self):
        return hash(tuple(self._register))

    def reset(self):
        self._register[:] = 0


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
