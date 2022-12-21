from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional

OPERATIONS: Dict[str, Callable[[float, float], float]] = {
    "*": lambda x, y: x * y,
    "/": lambda x, y: x / y,
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
}


class Monkey(ABC):

    @abstractmethod
    def get_value(self) -> float:
        pass

    @abstractmethod
    def scream(self) -> str:
        pass

    @classmethod
    def parse_horde(cls, data: List[str]) -> Dict[str, "Monkey"]:
        horde: Dict[str, Monkey] = {}
        for line in data:
            name, data = line.split(":")
            name = name.strip()
            data = data.strip()
            try:
                value = float(data)
                horde[name] = NumberMonkey(value=value)
            except ValueError:
                monkey1, operation, monkey2 = data.split(" ")
                horde[name] = MathMonkey(monkey1=monkey1, operation=operation, monkey2=monkey2, horde=horde)
        return horde

    def __str__(self):
        return f"{self.__class__.__name__} screaming {self.scream()}"


class NumberMonkey(Monkey):

    def __init__(self, value: float):
        self._value = value

    def get_value(self) -> float:
        return self._value

    def scream(self) -> str:
        return str(self._value)


class MathMonkey(Monkey):

    def __init__(self, monkey1: str, monkey2: str, operation: str, horde: Dict[str, Monkey]):
        self._monkey1 = monkey1
        self._monkey2 = monkey2
        self._operation = operation
        self._horde = horde
        self._cache = None

    @property
    def monkey1(self):
        return self._monkey1

    @property
    def monkey2(self):
        return self._monkey2

    @property
    def operation(self):
        return self._operation

    def get_value(self) -> float:
        if self._cache is None:
            v1 = self._horde[self._monkey1].get_value()
            v2 = self._horde[self._monkey2].get_value()
            if v1 is None or v2 is None:
                pass
            else:
                self._cache = OPERATIONS[self._operation](v1, v2)
        return self._cache

    def scream(self) -> str:
        return f"{self._monkey1} {self._operation} {self._monkey2}"


class EqualMonkey(Monkey):
    def __init__(self, monkey1: str, monkey2: str, horde: Dict[str, Monkey]):
        self._monkey1 = monkey1
        self._monkey2 = monkey2
        self._horde = horde
        self._cache = None

    @property
    def monkey1(self):
        return self._monkey1

    @property
    def monkey2(self):
        return self._monkey2

    def get_value(self) -> float:
        return self._horde[self.monkey1].get_value() == self._horde[self.monkey2].get_value()

    def scream(self) -> str:
        return f"{self.monkey1} equals to {self.monkey2}"


class HumanMonkey(NumberMonkey):

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @classmethod
    def solve(cls, horde: Dict[str, Monkey]) -> Optional[float]:
        human_monkeys = [x for x in horde.values() if isinstance(x, HumanMonkey)]
        if len(human_monkeys) != 1:
            raise Exception()
        human_monkey = human_monkeys[0]
        equal_monkeys = [x for x in horde.values() if isinstance(x, EqualMonkey)]
        if len(equal_monkeys) != 1:
            raise Exception()
        equal_monkey = equal_monkeys[0]

        human_monkey.value = None

        s1 = horde[equal_monkey.monkey1].get_value()
        s2 = horde[equal_monkey.monkey2].get_value()

        if s1 is not None and s2 is not None:
            return None
        if s1 is not None:
            human_side = equal_monkey.monkey2
            value = s1
        elif s2 is not None:
            human_side = equal_monkey.monkey1
            value = s2
        else:
            raise Exception()

        ret = cls._solve(horde=horde, target=value, monkey=horde[human_side])
        human_monkey.value = ret
        return ret

    @classmethod
    def _solve(cls, horde: Dict[str, Monkey], target: float, monkey: Monkey) -> Optional[float]:

        if isinstance(monkey, HumanMonkey):
            return target
        if not isinstance(monkey, MathMonkey):
            raise Exception()

        monkey: MathMonkey
        s1 = horde[monkey.monkey1].get_value()
        s2 = horde[monkey.monkey2].get_value()
        if s1 is not None and s2 is not None:
            return None
        if s1 is not None:
            human_side = monkey.monkey2
            value = invert(monkey.operation, target=target, value=s1, pos1=False)
        elif s2 is not None:
            human_side = monkey.monkey1
            value = invert(monkey.operation, target=target, value=s2, pos1=True)
        else:
            raise Exception()
        ret = cls._solve(horde=horde, target=value, monkey=horde[human_side])
        return ret


def invert(operation: str, target: float, value: float, pos1: bool):
    if operation == "+":
        return target - value
    if operation == "-":
        if pos1:
            return target + value
        else:
            return -target + value
    if operation == "*":
        return target / value
    if operation == "/":
        if pos1:
            return target * value
        else:
            return value / target
    raise Exception(f"Not invert-able: {operation}")
