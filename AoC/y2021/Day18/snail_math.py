from abc import ABC, abstractmethod
from enum import Enum, IntEnum
from typing import List, Iterable, Tuple, Optional, Any


class ReduceType(Enum):
    Explode = 1
    Split = 2


class Direction(IntEnum):
    Left = -1
    Right = 1


class SnailFishNumber(ABC):
    reduction_dtype = Tuple[bool, Optional[Tuple[ReduceType, Tuple[Any, ...]]]]

    def __init__(self):
        self._parent = None

    def set_parent(self, parent: "SnailFishNumber") -> "SnailFishNumber":
        self._parent = parent
        return self

    def get_parent(self) -> "SnailFishNumber":
        return self._parent

    def get_depth(self) -> int:
        return 0 if self.get_parent() is None else self.get_parent().get_depth() + 1

    @abstractmethod
    def need_reduction(self) -> bool:
        pass

    @abstractmethod
    def reduce(self, reduction_type: Optional[ReduceType] = None) -> reduction_dtype:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def offer(self, value: "RegularNumber", offering_number: "SnailFishNumber", direction: Direction) -> bool:
        pass

    @abstractmethod
    def get_magnitude(self) -> int:
        pass

    @abstractmethod
    def copy(self) -> "SnailFishNumber":
        pass

    @classmethod
    def parse(cls, data: str, auto_reduce: bool = True) -> "SnailFishNumber":
        data = data.strip()
        try:
            int_data = int(data)
            ret = RegularNumber(value=int_data)
        except ValueError:
            if data[0] != "[" or data[-1] != "]":
                raise ValueError(f"Could not parse {data} as a {cls.__name__}")

            current_child: List[str] = []
            found_children: List[List[str]] = []
            stack = 0
            for d in data[1:-1]:
                if d == "," and stack == 0:
                    found_children.append(current_child)
                    current_child = []
                else:
                    current_child.append(d)
                    if d == "[":
                        stack += 1
                    elif d == "]":
                        stack -= 1
            found_children.append(current_child)
            if stack != 0 or len(found_children) != 2 or any(len(x) == 0 for x in found_children):
                raise ValueError(f"Could not parse {data} as a {cls.__name__}")
            c1 = cls.parse(data="".join(found_children[0]), auto_reduce=False)
            c2 = cls.parse(data="".join(found_children[1]), auto_reduce=False)
            ret = PairNumber(c1, c2)
        if auto_reduce:
            ret = cls.auto_reduce(number=ret)
        return ret

    @classmethod
    def auto_reduce(cls, number: "SnailFishNumber") -> "SnailFishNumber":
        to_reduce = True
        while to_reduce:
            to_reduce, *_ = number.reduce(reduction_type=ReduceType.Explode)
            if to_reduce:
                continue
            to_reduce, *_ = number.reduce(reduction_type=ReduceType.Split)
        return number

    @classmethod
    def add(cls, n1: "SnailFishNumber", n2: "SnailFishNumber") -> "SnailFishNumber":
        ret = PairNumber(n1, n2)
        return cls.auto_reduce(number=ret)


class RegularNumber(SnailFishNumber):

    def __init__(self, value: int):
        super().__init__()
        self._value = value

    def get_value(self) -> int:
        return self._value

    def get_magnitude(self) -> int:
        return self.get_value()

    def offer(self, value: "RegularNumber", offering_number: "SnailFishNumber", direction: Direction) -> bool:
        self._value += value.get_value()
        return True

    def need_reduction(self) -> bool:
        if self.get_value() >= 10:
            return True

    def reduce(self, reduction_type: Optional[ReduceType] = None) -> SnailFishNumber.reduction_dtype:
        if self.need_reduction() and (reduction_type is None or reduction_type == ReduceType.Split):
            left = self.get_value() // 2
            right = self.get_value() - left
            left_number = RegularNumber(left)
            right_number = RegularNumber(right)
            new_number = PairNumber(left_number, right_number).set_parent(self.get_parent())
            return True, (ReduceType.Split, (new_number,))
        return False, None

    def __str__(self) -> str:
        return str(self.get_value())

    def copy(self) -> "SnailFishNumber":
        return self.__class__(self.get_value())


class PairNumber(SnailFishNumber):

    def __init__(self, *children: "SnailFishNumber"):
        super().__init__()
        if len(children) != 2:
            raise ValueError(f"I can only have 2 children. You wanted to give me {len(children)}")
        for c in children:
            c.set_parent(self)
        self._children: List[SnailFishNumber] = list(children)

    def get_magnitude(self) -> int:
        return 3 * self[0].get_magnitude() + 2 * self[1].get_magnitude()

    def offer(self, value: "RegularNumber", offering_number: "SnailFishNumber", direction: Direction) -> bool:
        try:
            i = self._children.index(offering_number)
            if direction == Direction.Left:
                idx: List[int] = list(range(i - 1, -1, -1))
            elif direction == Direction.Right:
                idx: List[int] = list(range(i + 1, len(self), 1))
            else:
                idx: List[int] = []
        except ValueError:
            idx = list(range(len(self)))
            if direction == Direction.Left:
                idx = idx[::-1]

        for j in idx:
            if self[j].offer(value=value, offering_number=self, direction=direction):
                return True
        par = self.get_parent()
        if par is not None:
            if par.offer(value=value, offering_number=self, direction=direction):
                return True
        return False

    def __getitem__(self, idx: int) -> SnailFishNumber:
        if 0 <= idx < len(self):
            return self._children[idx]
        raise ValueError(f"I only have {len(self)} children. You wanted to get the {idx + 1}.")

    def __len__(self):
        return len(self._children)

    def __iter__(self) -> Iterable[SnailFishNumber]:
        for i in range(len(self)):
            yield self[i]

    def need_reduction(self) -> bool:
        if self.get_depth() >= 4 and all(isinstance(x, RegularNumber) for x in self):
            return True
        return False

    def reduce(self, reduction_type: Optional[ReduceType] = None) -> SnailFishNumber.reduction_dtype:
        if self.need_reduction() and (reduction_type is None or reduction_type == ReduceType.Explode):
            return True, (ReduceType.Explode, (self[0], self[1]))

        for i in range(len(self)):
            number = self[i]
            reduced, data = number.reduce(reduction_type=reduction_type)
            if reduced:
                if data is not None:
                    typ, reduced_data = data
                    if typ == ReduceType.Split:
                        new_number: SnailFishNumber = reduced_data[0]
                        new_number.set_parent(self)
                        self._children[i] = new_number
                    elif typ == ReduceType.Explode:
                        left: RegularNumber = reduced_data[0]
                        right: RegularNumber = reduced_data[1]
                        self.offer(value=left, offering_number=number, direction=Direction.Left)
                        self.offer(value=right, offering_number=number, direction=Direction.Right)
                        self._children[i] = RegularNumber(value=0).set_parent(self)
                return True, None
        return False, None

    def __str__(self) -> str:
        return f"[{','.join(str(x) for x in self)}]"

    def copy(self) -> "SnailFishNumber":
        return self.__class__(*[x.copy() for x in self._children])
