import sys
import os.path
import uuid
from datetime import timedelta
from typing import Callable, AnyStr, Optional, Dict, List, Tuple, Iterable, Generator, Iterator, Set, Deque, Any, Type, \
    Union
from collections import defaultdict, OrderedDict, Counter
from time import perf_counter
from itertools import chain, product, combinations
from functools import lru_cache
from copy import deepcopy
from math import lcm, ceil, floor, prod
import re
from queue import PriorityQueue, Queue
from operator import xor
from abc import ABC, abstractmethod
from enum import Enum
from pprint import pformat, pprint

import matplotlib.pyplot as plt
from shapely import Polygon, Point, LineString
from tqdm import tqdm, trange
import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor
import networkx as nx
import graphblas_algorithms as ga
from networkx.drawing.nx_pydot import graphviz_layout
from scipy.interpolate import KroghInterpolator, BarycentricInterpolator, lagrange
from networkx.algorithms.dag import transitive_closure

from ..Day17 import tpl_add, tpl_mult, tpl_dist

# noinspection DuplicatedCode
DAY = int(os.path.basename(os.path.dirname(__file__))[3:])
YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[1:])

RENDER = True

SLOPES = {
    "<": (-1, 0),
    ">": (1, 0),
    "v": (0, 1),
    "^": (0, -1),
}


@Preprocessor(year=YEAR, day=DAY)
def preproc_1(data: List[str]) -> nx.Graph:
    g: nx.Graph = nx.Graph()
    for line in (x.strip() for x in data if len(x.strip()) > 0):
        n1, nodes = line.split(":")
        n1 = n1.strip()
        for n2 in nodes.strip().split(" "):
            g.add_edge(n1, n2)
            # g.add_edge(n2, n1)
    return g


@Task(year=YEAR, day=DAY, task=1, extra_config={"max_cuts": 3})
def task_01(g: nx.Graph, log: Callable[[AnyStr], None], max_cuts: int):
    log(f"There are {len(g.nodes)} and {len(g.edges)} connections")

    log(f"Checking wich {max_cuts} edges are most important")
    t1 = perf_counter()
    edge_importance = sorted(nx.edge_betweenness_centrality(g).items(), key=lambda x: x[1], reverse=True)
    most_vital_edges = [x[0] for x in edge_importance[:max_cuts]]
    t2 = perf_counter()

    log(f"Took {timedelta(seconds=t2-t1)} to calculate most important connections")
    log(f"The {max_cuts} most important edges are {', '.join(str(x) for x in most_vital_edges)}")

    g2 = g.copy(as_view=False)
    g2.remove_edges_from(most_vital_edges)
    cc = list(nx.connected_components(g2))

    cc_size = [len(x) for x in cc]

    log(f"When cutting the most important edges {len(cc)} distinct areas are created of sizes {cc_size}")

    return prod(cc_size)


@Task(year=YEAR, day=DAY, task=2)
def task_02(data: List[Tuple[Tuple[int, int, int], Tuple[int, int, int]]], log: Callable[[AnyStr], None]):
    log(f"You are good to go")
    return "Merry christmas"
