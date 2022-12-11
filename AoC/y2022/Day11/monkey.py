from abc import ABC, abstractmethod
from typing import List, Any, Dict, Tuple, Callable, Type
from dataclasses import dataclass
from copy import deepcopy

import numpy as np


VALUE_TYPE = int


@dataclass
class Item:
    value: VALUE_TYPE

    def __str__(self):
        return str(self.value)


class Operation:

    OPERATIONS = {
        "*": lambda x, y: VALUE_TYPE(x * y),
        "/": lambda x, y: VALUE_TYPE(x / y),
        "+": lambda x, y: VALUE_TYPE(x + y),
        "-": lambda x, y: VALUE_TYPE(x - y),
    }

    def __init__(self, values: List[str], operations: List[str]):
        if len(values) - 1 != len(operations):
            raise Exception(f"{values}, {operations}")
        self._values = values.copy()
        self._operations = operations.copy()

    def _get_value(self, i, typ: Type = int, **kwargs):
        try:
            return typ(self._values[i].strip())
        except ValueError:
            return typ(kwargs[self._values[i].strip()])

    def execute(self, **kwargs):
        current: float = self._get_value(0, typ=VALUE_TYPE, **kwargs)
        _tmp = current
        for i in range(len(self._operations)):
            v = self._get_value(i+1, typ=VALUE_TYPE, **kwargs)
            op = self._operations[i].strip()
            current = self.__class__.OPERATIONS[op](current, v)
        return current

    def __str__(self):
        ret = [self._values[0]]
        for i in range(len(self._operations)):
            ret.append(self._operations[i])
            ret.append(self._values[i+1])
        return " ".join(ret)

    @classmethod
    def parse(cls, line: str) -> "Operation":
        line = line.strip()
        t, data = line.split(":", 1)
        t = t.strip()
        if t != "Operation":
            raise Exception()
        t, data = data.strip().split("=")
        t = t.strip()
        if t != "new":
            raise Exception()
        data = data.strip().split(" ")
        values = [data[0]]
        operations = []
        for i in range(1, len(data), 2):
            operations.append(data[i])
            values.append(data[i+1])
        return Operation(values=values, operations=operations)


class Condition(ABC):
    @abstractmethod
    def execute(self, value: VALUE_TYPE) -> bool:
        pass

    @abstractmethod
    def __str__(self):
        pass

    @classmethod
    @abstractmethod
    def parse(cls, line: str) -> "Condition":
        pass


class DivisibleCondition(Condition):

    def __init__(self, value: VALUE_TYPE):
        self._value = value

    @property
    def value(self):
        return self._value

    def execute(self, value: VALUE_TYPE) -> bool:
        return value % self._value == 0

    def __str__(self):
        return f"item is divisible by {self._value}"

    @classmethod
    def parse(cls, line: str) -> "DivisibleCondition":
        line = line.strip()
        t, data = line.split(":", 1)
        t = t.strip()
        if t != "Test":
            raise Exception()
        data = str(data).strip()
        if not data.startswith("divisible by "):
            raise Exception()
        return DivisibleCondition(value=int(data[len("divisible by "):]))


class Target(ABC):

    @abstractmethod
    def execute(self, item: Item, monkeys: Dict[int, "Monkey"]):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @classmethod
    @abstractmethod
    def parse(cls, line: str) -> "Target":
        pass


class MonkeyTarget(Target):

    def __init__(self, target_monkey: int):
        self._target_monkey = target_monkey

    def execute(self, item: Item, monkeys: Dict[int, "Monkey"]):
        monkeys[self._target_monkey].add_item(item=item)

    def __str__(self):
        return f"throw to monkey {self._target_monkey}"

    @classmethod
    def parse(cls, line: str) -> "MonkeyTarget":
        line = line.strip()
        t, data = line.split(":", 1)
        t = t.strip()
        if t not in ("If true", "If false"):
            raise Exception(f'{t} not in {("If true", "If false")}')
        data = str(data).strip()
        if not data.startswith("throw to monkey "):
            raise Exception()
        return MonkeyTarget(target_monkey=int(data[len("throw to monkey "):]))


class Monkey:
    def __init__(self, items: List[Item], operation: Operation, condition: Condition, targets: Dict[bool, Target],
                 monkey_horde: Dict[int, "Monkey"]):
        self._items = items
        self._operation = operation
        self._condition = condition
        self._targets = targets
        self._monkey_horde = monkey_horde

    @property
    def items(self):
        return self._items

    @property
    def operation(self):
        return self._operation

    @property
    def condition(self):
        return self._condition

    def add_item(self, item: Item):
        self._items.append(item)

    def execute(self, relief_callback: Callable[[Item], Item]) -> int:
        ret = 0
        while len(self._items) > 0:
            item = self._items.pop(0)
            item.value = self._operation.execute(old=item.value)
            if item.value != round(item.value, 0):
                raise Exception(f"{item.value}")
            item = relief_callback(item)
            condition = self._condition.execute(value=item.value)
            self._targets[condition].execute(item=item, monkeys=self._monkey_horde)
            ret += 1
        return ret

    def __str__(self):
        return f"Monkey has {', '.join(str(x) for x in self._items)} will do {self._operation} check if {self._condition} and then {' or '.join(f'{v} if {k}' for k, v in self._targets.items())}, he has {len(self._monkey_horde) - 1} friends"

    @classmethod
    def parse(cls, lines: List[str], monkey_horde: Dict[int, "Monkey"]) -> Tuple[int, "Monkey"]:
        line = lines[0].strip()
        if not line.startswith("Monkey"):
            raise Exception()

        monkey_id = int(line[len("Monkey "):-1].strip())
        items, operation, condition, targets = None, None, None, {}

        i = 1
        while i < len(lines):
            line = lines[i].rstrip()
            if line.strip().startswith("Starting items:"):
                items_raw = line.strip()[len("Starting items:"):].strip().split(",")
                items = [Item(value=VALUE_TYPE(x.strip())) for x in items_raw]
            if line.strip().startswith("Operation:"):
                operation = Operation.parse(line=line)
            if line.strip().startswith("Test:"):
                for c in Condition.__subclasses__():
                    # noinspection PyBroadException
                    try:
                        condition = c.parse(line=line)
                        break
                    except Exception:
                        pass
                if condition is None:
                    raise Exception()
                for _ in range(2):
                    i += 1
                    c_line = lines[i].rstrip()
                    k = {
                        "    If true": True,
                        "    If false": False,
                    }[c_line.split(":", 1)[0]]
                    for c in Target.__subclasses__():
                        # noinspection PyBroadException
                        try:
                            targets[k] = c.parse(line=c_line)
                            break
                        except Exception as e:
                            # print(e)
                            raise
                    if k not in targets:
                        raise Exception()

            i += 1

        monkey = Monkey(items=items, operation=operation, condition=condition, targets=targets, monkey_horde=monkey_horde)

        return monkey_id, monkey


def load_monkeys(lines: List[str]) -> Dict[int, "Monkey"]:
    lines = lines + [""]
    monkey_horde: Dict[int, "Monkey"] = {}
    i = 0
    cur_monkey: List[str] = []
    while i < len(lines):
        line = lines[i]

        if len(line.strip()) <= 0:
            if len(cur_monkey) > 0:
                monkey_id, monkey = Monkey.parse(lines=cur_monkey, monkey_horde=monkey_horde)
                monkey_horde[monkey_id] = monkey
            cur_monkey = []
        else:
            cur_monkey.append(line)

        i += 1

    return monkey_horde
