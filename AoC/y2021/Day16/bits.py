from abc import ABC, abstractmethod
from typing import Optional, Type, List, Tuple, Iterable, Dict

import numpy as np


class BuoyancyInterchangeTransmissionPacket(ABC):
    _identification: Dict[int, Type["BuoyancyInterchangeTransmissionPacket"]] = {}

    @classmethod
    def register(cls, typ: int, packet: Type["BuoyancyInterchangeTransmissionPacket"], force: bool = False):
        if typ in cls._identification and not force:
            raise KeyError(f"packet for {typ} already registered")
        cls._identification[typ] = packet

    def __init__(self, version: int, typ: int, data: np.ndarray):
        self._data = data
        self._version = version
        self._typ = typ

    def get_data(self) -> np.ndarray:
        return self._data.copy()

    @staticmethod
    def bin_to_int(data: Iterable[int]) -> int:
        return int("".join(str(x) for x in data), 2)

    def get_version(self) -> int:
        return self._version

    def get_version_sum(self) -> int:
        return self._version

    def get_tyo(self) -> int:
        return self._typ

    def __len__(self) -> int:
        return self._data.shape[0]

    @abstractmethod
    def get_value(self) -> int:
        pass

    @abstractmethod
    def get_depth(self) -> int:
        pass

    @abstractmethod
    def get_packet_count(self) -> int:
        pass

    @abstractmethod
    def summary(self, indentation: int = 2) -> str:
        pass

    @classmethod
    def parse(cls, data: np.ndarray) -> Tuple[Optional["BuoyancyInterchangeTransmissionPacket"], int]:
        if (data == 0).all():
            return None, -1
        version = cls.bin_to_int(data=data[:3])
        typ = cls.bin_to_int(data=data[3:6])
        packet_class = cls.identify(typ=typ)
        packet = packet_class(version, typ, data)
        return packet, len(packet)

    @classmethod
    def identify(cls, typ: int) -> Type["BuoyancyInterchangeTransmissionPacket"]:
        return cls._identification[typ]

    def __str__(self):
        return f"{self.__class__.__name__}: {self.get_value()}"

    def __repr__(self):
        return f"<{self.__class__.__name__}-{self.get_version()}, v: {self.get_value()}, l: {len(self)}>"


register = BuoyancyInterchangeTransmissionPacket.register


class LiteralPackage(BuoyancyInterchangeTransmissionPacket):

    def __init__(self, version: int, typ: int, data: np.ndarray):
        i = 6
        value: List[int] = []
        while True:
            value.extend(data[i + 1:i + 5])
            i += 5
            if data[i - 5] == 0:
                break
        self._value = self.bin_to_int(data=value)
        super().__init__(version, typ, data[:i])

    def get_value(self) -> int:
        return self._value

    def get_depth(self) -> int:
        return 1

    def get_packet_count(self) -> int:
        return 1

    def summary(self, indentation: int = 2) -> str:
        return str(self)


class OperatorPackage(BuoyancyInterchangeTransmissionPacket):

    def __init__(self, version: int, typ: int, data: np.ndarray):
        from .operators import get_operator
        self._sub_packets: List[BuoyancyInterchangeTransmissionPacket] = []

        self._my_op = get_operator(typ=typ)()

        length_type: int = data[6]
        if length_type == 0:
            offset = 7 + 15
            sub_packets_len = self.bin_to_int(data[7:offset])
            length = offset + sub_packets_len
            n = np.inf
            sub_packets_data = data[offset:length]
        elif length_type == 1:
            offset = 7 + 11
            length = None
            n = self.bin_to_int(data[7:offset])
            sub_packets_data = data[offset:]
        else:
            raise ValueError(f"Cant handle {length_type=}")

        j = 0
        while True:
            if j >= n:
                break
            j += 1
            sub_packet, lsp = self.parse(data=sub_packets_data)
            if sub_packet is None:
                break
            self._sub_packets.append(sub_packet)
            sub_packets_data = sub_packets_data[lsp:]

        if length is None:
            length = offset + sum(len(x) for x in self._sub_packets)

        super().__init__(version, typ, data[:length])

    def get_version_sum(self) -> int:
        ret = self.get_version()
        for p in self._sub_packets:
            ret += p.get_version_sum()
        return ret

    def get_value(self) -> int:
        return self._my_op(self._sub_packets)

    def get_depth(self) -> int:
        return max([x.get_depth() for x in self._sub_packets] + [0]) + 1

    def get_packet_count(self) -> int:
        return sum([x.get_packet_count() for x in self._sub_packets] + [0]) + 1

    def __repr__(self):
        return f"<{self.__class__.__name__}-{self.get_version()}, " \
               f"v: {self.get_value()}, l: {len(self)}, p: {len(self._sub_packets)}>"

    def __str__(self):
        return f"{self.__class__.__name__}[{str(self._my_op)}]: " \
               f"{self._my_op.print(packets=[x.get_value() for x in self._sub_packets])} = {self.get_value()}"

    def summary(self, indentation: int = 2) -> str:
        ret: List[str] = [str(self)]
        # │ ─ ├
        template = "{f}{v}{t}"
        for i, package in enumerate(self._sub_packets):
            package_summary = package.summary()
            for j, line in enumerate(package_summary.split("\n")):
                if j == 0:
                    if i < len(self._sub_packets) - 1:
                        f = "├"
                    else:
                        f = "└"
                    v = "─"
                else:
                    if i < len(self._sub_packets) - 1:
                        f = "│"
                    else:
                        f = " "
                    v = " "

                ret.append(template.format(f=f, v=v, t=line))

        return "\n".join(ret)


for _ in range(10):
    register(typ=_, packet=OperatorPackage, force=False)
register(typ=4, packet=LiteralPackage, force=True)
