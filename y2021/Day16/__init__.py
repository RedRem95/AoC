import os.path
from typing import Any, Optional, List

import numpy as np
from AoC_Companion.Day import Day, TaskResult

from .bits import BuoyancyInterchangeTransmissionPacket as Bits


class Day16(Day):

    def __init__(self, year: int, create_summary: bool = True):
        super().__init__(year)
        self._create_summary = create_summary

    def pre_process_input(self, data: Any) -> Any:
        data: List[str] = super().pre_process_input(data=data)
        data = [x for x in data if len(x) > 0]
        bin_str = "".join('{0:04b}'.format(int(x, 16)) for x in data[0])
        ret = np.array([int(x) for x in bin_str], dtype=np.uint8)
        return ret

    def run_t1(self, data: np.ndarray) -> Optional[TaskResult]:
        packet, *_ = Bits.parse(data=data.copy())
        ret = packet.get_version_sum()
        log = [
            f"The data had {packet.get_packet_count()} packets and a max depth of {packet.get_depth()}",
            f"Root package has a length of {len(packet)} bits. Input has a length of {data.shape[0]} bits",
            f"Sum of versions {ret}"
        ]
        return TaskResult(ret, log=log)

    def run_t2(self, data: np.ndarray) -> Optional[TaskResult]:
        packet, *_ = Bits.parse(data=data.copy())
        ret = packet.get_value()
        log = [
            f"The data had {packet.get_packet_count()} packets and a max depth of {packet.get_depth()}",
            f"Root package has a length of {len(packet)} bits. Input has a length of {data.shape[0]} bits",
            f"Value of root package {ret}"
        ]
        if self._create_summary:
            with open(os.path.join(os.path.dirname(__file__), "summary.txt"), "wb") as f_out:
                f_out.write(packet.summary().encode("utf-8"))
        return TaskResult(ret, log=log)
