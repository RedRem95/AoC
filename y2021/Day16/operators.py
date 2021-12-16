from abc import ABC, abstractmethod
from typing import List, Dict, Type, Any, Union

import numpy as np

from y2021.Day16.bits import BuoyancyInterchangeTransmissionPacket


class BuoyancyInterchangeTransmissionOperator(ABC):
    _operator_map: Dict[int, Type["BuoyancyInterchangeTransmissionOperator"]] = {}

    @classmethod
    def register(cls, typ: int, operator: Type["BuoyancyInterchangeTransmissionOperator"], force: bool = False):
        if typ in cls._operator_map and not force:
            raise KeyError(f"operator for {typ} already registered")
        cls._operator_map[typ] = operator

    @classmethod
    def get_operator(cls, typ: int) -> Type["BuoyancyInterchangeTransmissionOperator"]:
        return cls._operator_map[typ]

    def __init__(self, *args, **kwargs):
        pass

    def __str__(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def print(self, packets: List[Any]) -> str:
        pass

    @abstractmethod
    def __call__(self, packets: List[BuoyancyInterchangeTransmissionPacket]) -> int:
        pass


class ValidationOperator(BuoyancyInterchangeTransmissionOperator, ABC):
    class ValidationError(Exception):
        pass

    def print(self, packets: List[Any]) -> str:
        if not self._validate(packets=packets):
            raise ValidationOperator.ValidationError(f"Could not print {self}, validation of packets failed")
        return self._print_validated(packets=packets)

    def __call__(self, packets: List[BuoyancyInterchangeTransmissionPacket]) -> int:
        if not self._validate(packets=packets):
            raise ValidationOperator.ValidationError(f"Could not calculate {self}, validation of packets failed")
        return self._call_validated(packets=packets)

    @abstractmethod
    def _validate(self, packets: List[Union[Any, BuoyancyInterchangeTransmissionPacket]]) -> bool:
        pass

    @abstractmethod
    def _print_validated(self, packets: List[Any]) -> str:
        pass

    @abstractmethod
    def _call_validated(self, packets: List[BuoyancyInterchangeTransmissionPacket]) -> int:
        pass


register = BuoyancyInterchangeTransmissionOperator.register
get_operator = BuoyancyInterchangeTransmissionOperator.get_operator


class SumOp(BuoyancyInterchangeTransmissionOperator):

    def __call__(self, packets: List[BuoyancyInterchangeTransmissionPacket]) -> int:
        return sum(x.get_value() for x in packets)

    def print(self, packets: List[Any]) -> str:
        return f" + ".join(str(x) for x in packets)


class ProdOp(BuoyancyInterchangeTransmissionOperator):

    def __call__(self, packets: List[BuoyancyInterchangeTransmissionPacket]) -> int:
        return int(np.prod([x.get_value() for x in packets]))

    def print(self, packets: List[Any]) -> str:
        return f" * ".join(str(x) for x in packets)


class MinOp(BuoyancyInterchangeTransmissionOperator):

    def __call__(self, packets: List[BuoyancyInterchangeTransmissionPacket]) -> int:
        return min(x.get_value() for x in packets)

    def print(self, packets: List[Any]) -> str:
        return f"MIN({', '.join(str(x) for x in packets)})"


class MaxOp(BuoyancyInterchangeTransmissionOperator):

    def __call__(self, packets: List[BuoyancyInterchangeTransmissionPacket]) -> int:
        return max(x.get_value() for x in packets)

    def print(self, packets: List[Any]) -> str:
        return f"MAX({', '.join(str(x) for x in packets)})"


class GreaterThanOp(ValidationOperator):

    def _validate(self, packets: List[Union[Any, BuoyancyInterchangeTransmissionPacket]]) -> bool:
        return len(packets) == 2

    def _print_validated(self, packets: List[Any]) -> str:
        return f"{packets[0]} > {packets[1]}"

    def _call_validated(self, packets: List[BuoyancyInterchangeTransmissionPacket]) -> int:
        return int(packets[0].get_value() > packets[1].get_value())


class LessThanOp(GreaterThanOp):

    def _print_validated(self, packets: List[Any]) -> str:
        return f"{packets[0]} < {packets[1]}"

    def _call_validated(self, packets: List[BuoyancyInterchangeTransmissionPacket]) -> int:
        return int(packets[0].get_value() < packets[1].get_value())


class EqualToOp(GreaterThanOp):

    def _print_validated(self, packets: List[Any]) -> str:
        return f"{packets[0]} == {packets[1]}"

    def _call_validated(self, packets: List[BuoyancyInterchangeTransmissionPacket]) -> int:
        return int(packets[0].get_value() == packets[1].get_value())


register(0, SumOp)
register(1, ProdOp)
register(2, MinOp)
register(3, MaxOp)
register(5, GreaterThanOp)
register(6, LessThanOp)
register(7, EqualToOp)
