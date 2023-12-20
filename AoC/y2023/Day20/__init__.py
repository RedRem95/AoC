import sys
import os.path
from datetime import timedelta
from typing import Callable, AnyStr, Optional, Dict, List, Tuple, Iterable, Generator, Iterator, Set, Deque, Any, Type
from collections import defaultdict, OrderedDict, Counter
from time import perf_counter
from itertools import chain
from functools import lru_cache
from copy import deepcopy
from math import lcm, ceil, prod
import re
from queue import PriorityQueue, Queue
from operator import xor
from abc import ABC, abstractmethod
from enum import Enum
from pprint import pformat, pprint

import matplotlib.pyplot as plt
from shapely import Polygon, Point, LineString
from tqdm import tqdm
import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout

from ..Day17 import tpl_add, tpl_mult, tpl_dist

# noinspection DuplicatedCode
DAY = int(os.path.basename(os.path.dirname(__file__))[3:])
YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[1:])

RENDER = True


@Preprocessor(year=YEAR, day=DAY)
def preproc_1(data: List[str]):
    print("preproc")
    modules: Dict[str, "Module"] = {}
    my_queue = []
    for line in (x.strip() for x in data if len(x.strip()) > 0):
        module, targets = line.split("->")
        module = module.strip()
        if module == "broadcaster":
            module_type: Type[Module] = Broadcast
            module_name = module
        else:
            module_type: Type[Module] = {"%": FlipFlop, "&": Conjunction}[module[0]]
            module_name = module[1:]
        if module_name in modules:
            raise Exception()
        modules[module_name] = module_type(pulse_send_queue=my_queue, name=module_name)
        for t in (x.strip() for x in targets.strip().split(",")):
            modules[module_name].add_output(t)
    if "button" in modules:
        raise Exception()
    modules["button"] = Button(name="button", pulse_send_queue=my_queue)
    modules["button"].add_output("broadcaster")

    for missing_out in (x for x in set().union(*[x.iter_out() for x in modules.values()]) if x not in modules):
        modules[missing_out] = Output(name=missing_out, pulse_send_queue=my_queue)

    for m in modules.values():
        for o in m.iter_out():
            modules[o].add_input(m.name)

    return modules, my_queue, "button"


@Task(year=YEAR, day=DAY, task=1)
def task_01(data: Tuple[Dict[str, "Module"], List, str], log: Callable[[AnyStr], None]):
    num_pushes: int = 1000
    network, my_queue, init_module = data
    log(f"Processing a network of {len(network)} modules")
    glob_pulse_counter = Counter({x: 0 for x in Pulse})
    for _ in range(num_pushes):
        pulse_counter = process_network(network=network, queue=my_queue, init_module=init_module,
                                        log=lambda *args: None,
                                        init_kwargs=lambda: {"origin": None, "pulse": None})
        glob_pulse_counter.update(pulse_counter)

    log(f"After {num_pushes} button presses "
        f"{', '.join(f'{p.name}-Pulses happened {glob_pulse_counter[p]} times' for p in Pulse)}")

    return prod(glob_pulse_counter.values())


@Task(year=YEAR, day=DAY, task=2, extra_config={"render": RENDER})
def task_02(data: Tuple[Dict[str, "Module"], List, str], log: Callable[[AnyStr], None], render: bool):
    network, my_queue, init_module = data
    log(f"Processing a network of {len(network)} modules")

    final_machine_key = "rx"

    # Replacing rx thingy with the FinalMachine
    log(f"Replacing machine {final_machine_key} with a {FinalMachine.__name__} that waits for a {Pulse.LOW.name}-Pulse")
    new_machine = FinalMachine(name=final_machine_key, pulse_send_queue=my_queue)

    # Check if Final machine ant the input if it matches the assumptions of only one input and a conjunction
    for o in network[final_machine_key].iter_out():
        new_machine.add_output(o)
    for i in network[final_machine_key].iter_in():
        new_machine.add_input(i)
    network[final_machine_key] = new_machine

    if len(list(new_machine.iter_in())) != 1:
        raise Exception(f"Cant do processing if {new_machine} has more than one input")

    # noinspection PyTypeChecker
    new_machine_in_conj: Conjunction = network[list(new_machine.iter_in())[0]]

    if not isinstance(new_machine_in_conj, Conjunction):
        raise Exception(f"Can only do processing if {new_machine} input is {Conjunction.__name__} "
                        f"({new_machine_in_conj.__class__.__name__} detected)")

    log(f"Only input of {new_machine} is {new_machine_in_conj}")
    log(f"Searching for loops in all {len(list(new_machine_in_conj.iter_in()))} inputs of {new_machine_in_conj} "
        f"to know when {new_machine} gets activated")

    # Setup watch callback on last conjunction to find loops in inputs
    watching: Dict[str, List[int]] = {k: [] for k in new_machine_in_conj.iter_in()}

    step_count = [0]

    def callback(origin: str, pulse: "Pulse"):
        if pulse == Pulse.HIGH:
            watching[origin].append(step_count[0])
            # log(f"Callback called from {origin}@{step_count[0]}")

    new_machine_in_conj.register_callback(callback=callback)

    # Process network step by step until all inputs have at least one loop
    while True:
        process_network(network=network, queue=my_queue, init_module=init_module,
                        log=lambda *args: None,
                        init_kwargs=lambda: {"origin": None, "pulse": None})

        if all(len(x) >= 2 for x in watching.values()):
            break

        step_count[0] += 1

    log(f"Did {step_count[0]} steps to find a loop in every input of {new_machine_in_conj}")
    ret = lcm(*[x[-1] - x[-2] for x in watching.values()])
    log(f"Lowest amount of button presses to activate the machine is {ret}")

    if render:
        colored_nodes: Dict[str, List[str]] = defaultdict(list)
        edges: List[Tuple[str, str]] = []
        for m in network.values():
            colored_nodes[m.color()].append(m.name)
            edges.extend((m.name, network[n].name) for n in m.iter_out())

        plt.figure(figsize=(20, 20))
        g = nx.DiGraph()
        g.add_edges_from(edges)
        layout = graphviz_layout(g, prog="dot")
        for c, nodes in colored_nodes.items():
            nx.draw_networkx_nodes(g, layout, nodelist=nodes, node_color=c)
        nx.draw_networkx_labels(g, layout)
        nx.draw_networkx_edges(g, layout)
        fig_path = os.path.join(os.path.dirname(__file__), "network.png")
        plt.savefig(fig_path)
        log(f"Figure saved to {fig_path}")

    return ret


def process_network(
        network: Dict[str, "Module"],
        queue: List[Tuple[str, str, "Pulse"]],
        log: Callable[[AnyStr], None],
        init_module: str, init_kwargs: Callable[[], Dict[str, Any]]
) -> Dict["Pulse", int]:
    if len(queue) > 0:
        raise Exception()

    counter = {x: 0 for x in Pulse}

    network[init_module].handle_pulse(**init_kwargs())

    while len(queue) > 0:
        sending_module, next_module, next_pulse = queue.pop(0)
        counter[next_pulse] += 1
        log(f"{sending_module} -{next_pulse.name}-> {next_module}")
        network[next_module].handle_pulse(origin=sending_module, pulse=next_pulse)

    return counter


class Pulse(Enum):
    LOW = 0,
    HIGH = 1


class Module(ABC):
    _PULSE_STORE: Dict[Pulse, int] = defaultdict(lambda: 0)

    @classmethod
    def _store_pulse(cls, pulse: Pulse):
        cls._PULSE_STORE[pulse] += 1

    def __init__(self, name: str, pulse_send_queue: List[Tuple[str, str, Pulse]]):
        self._pulse_send_queue = pulse_send_queue
        self._inputs: Set[str] = set()
        self._outputs: List[str] = []
        self._name = name
        self._callbacks: List[Callable[[str, Pulse], None]] = []

    @property
    def name(self):
        return self._name

    def add_input(self, inp: str):
        self._inputs.add(inp)

    def add_output(self, out: str):
        self._outputs.append(out)

    def iter_in(self) -> Iterator[str]:
        return self._inputs.__iter__()

    def iter_out(self) -> Iterator[str]:
        return self._outputs.__iter__()

    def handle_pulse(self, origin: str, pulse: Pulse):
        self._store_pulse(pulse=pulse)
        for c in self._callbacks:
            c(origin, pulse)
        snd = self._handle_pulse_abs(origin=origin, pulse=pulse)
        for o in self.iter_out():
            self._send_pulse_to(target=o, pulse=snd)

    def register_callback(self, callback: Callable[[str, Pulse], None]):
        self._callbacks.append(callback)

    @abstractmethod
    def _handle_pulse_abs(self, origin: str, pulse: Pulse) -> Optional[Pulse]:
        raise NotImplementedError()

    def _send_pulse_to(self, target: str, pulse: Pulse):
        if pulse is not None:
            self._pulse_send_queue.append((self.name, target, pulse))

    @abstractmethod
    def color(self) -> str:
        return "#fff"

    def __str__(self):
        return f"{self.__class__.__name__}-Module {self.name}"


class FlipFlop(Module):

    def __init__(self, name: str, pulse_send_queue: List[Tuple[str, str, Pulse]]):
        super().__init__(name=name, pulse_send_queue=pulse_send_queue)
        self._on_off = False

    def _handle_pulse_abs(self, origin: str, pulse: Pulse) -> Optional[Pulse]:
        if pulse == Pulse.HIGH:
            return None
        self._on_off = not self._on_off
        return Pulse.HIGH if self._on_off else Pulse.LOW

    def color(self) -> str:
        return "#fff700"


class Conjunction(Module):

    def __init__(self, name: str, pulse_send_queue: List[Tuple[str, str, Pulse]]):
        super().__init__(name=name, pulse_send_queue=pulse_send_queue)
        self._memory: Dict[str, Pulse] = defaultdict(lambda: Pulse.LOW)

    def _handle_pulse_abs(self, origin: str, pulse: Pulse) -> Optional[Pulse]:
        self._memory[origin] = pulse
        return self.state

    @property
    def state(self) -> Pulse:
        return Pulse.LOW if all(self._memory[x] == Pulse.HIGH for x in self.iter_in()) else Pulse.HIGH

    def color(self) -> str:
        return "#26580f"


class Broadcast(Module):

    def __init__(self, name: str, pulse_send_queue: List[Tuple[str, str, Pulse]]):
        super().__init__(name=name, pulse_send_queue=pulse_send_queue)

    def _handle_pulse_abs(self, origin: str, pulse: Pulse) -> Optional[Pulse]:
        return pulse

    def color(self) -> str:
        return "#0e4c92"


class Button(Module):

    def __init__(self, name: str, pulse_send_queue: List[Tuple[str, str, Pulse]]):
        super().__init__(name=name, pulse_send_queue=pulse_send_queue)

    def _handle_pulse_abs(self, origin: str, pulse: Pulse) -> Optional[Pulse]:
        return Pulse.LOW

    def color(self) -> str:
        return "#ff2400"


class Output(Module):

    def __init__(self, name: str, pulse_send_queue: List[Tuple[str, str, Pulse]]):
        super().__init__(name=name, pulse_send_queue=pulse_send_queue)

    def _handle_pulse_abs(self, origin: str, pulse: Pulse) -> Optional[Pulse]:
        return None

    def color(self) -> str:
        return "#000"


class FinalMachine(Module):

    def __init__(self, name: str, pulse_send_queue: List[Tuple[str, str, Pulse]]):
        super().__init__(name=name, pulse_send_queue=pulse_send_queue)
        self._memory: List[Pulse] = []

    def _handle_pulse_abs(self, origin: str, pulse: Pulse) -> Optional[Pulse]:
        self._memory.append(pulse)
        return None

    def memory_iter(self) -> Iterator[Pulse]:
        return self._memory.__iter__()

    def color(self) -> str:
        return "#000"
