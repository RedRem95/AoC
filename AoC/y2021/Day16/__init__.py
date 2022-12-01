from typing import Callable, AnyStr, List, Any, Optional, Dict, Tuple, Iterable, Set, Union
import os
import json
import enum
from queue import LifoQueue

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

from .bits import BuoyancyInterchangeTransmissionPacket as Bits


@Preprocessor(year=2021, day=16)
def pre_process_input(data: Any) -> Any:
    data = [x for x in data if len(x) > 0]
    bin_str = "".join('{0:04b}'.format(int(x, 16)) for x in data[0])
    ret = np.array([int(x) for x in bin_str], dtype=np.uint8)
    return ret


@Task(year=2021, day=16, task=1)
def run_t1(data: np.ndarray, log: Callable[[str], None]) -> Any:
    packet, *_ = Bits.parse(data=data.copy())
    log(f"The data had {packet.get_packet_count()} packets and a max depth of {packet.get_depth()}")
    log(f"Root package has a length of {len(packet)} bits. Input has a length of {data.shape[0]} bits")
    ret = packet.get_version_sum()
    log(f"Sum of versions {ret}")
    return ret


@Task(year=2021, day=16, task=2, extra_config={"create_summary": True})
def run_t2(data: np.ndarray, log: Callable[[str], None], create_summary: bool = False) -> Any:
    packet, *_ = Bits.parse(data=data.copy())
    log(f"The data had {packet.get_packet_count()} packets and a max depth of {packet.get_depth()}")
    log(f"Root package has a length of {len(packet)} bits. Input has a length of {data.shape[0]} bits")
    ret = packet.get_value()
    log(f"Value of root package {ret}")
    if create_summary:
        with open(os.path.join(os.path.dirname(__file__), "summary.txt"), "wb") as f_out:
            f_out.write(packet.summary().encode("utf-8"))
    return ret
