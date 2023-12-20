import sys
import os.path
from datetime import timedelta
from typing import Callable, AnyStr, Optional, Dict, List, Tuple, Iterable, Generator, Iterator, Set, Deque
from collections import defaultdict, OrderedDict
from time import perf_counter
from itertools import chain
from functools import lru_cache
from copy import deepcopy
from math import lcm, ceil, prod
import re
from queue import PriorityQueue, Queue
from operator import xor

from shapely import Polygon, Point, LineString
from tqdm import tqdm
import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

from ..Day17 import tpl_add, tpl_mult, tpl_dist

# noinspection DuplicatedCode
DAY = int(os.path.basename(os.path.dirname(__file__))[3:])
YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[1:])

RENDER = True


@Preprocessor(year=YEAR, day=DAY)
def preproc_1(data: List[str]):
    in_rules = True
    ret_rules: Dict[str, Tuple[List[Tuple[bool, str, int, str]], str]] = {}
    parts: List[Dict[str, int]] = []
    for line in (x.strip() for x in data):
        if len(line) <= 0:
            in_rules = False
            continue
        if in_rules:
            line = line[:-1]
            rule_name, rules = line.split("{")
            default = None
            parsed_rules = []
            for rule in (r.strip() for r in rules.split(",")):
                rule: str
                if ":" in rule:
                    rule, target = rule.split(":")
                    if "<" in rule:
                        parsed_rules.append((True, rule.split("<")[0], int(rule.split("<")[1]), target))
                    elif ">" in rule:
                        parsed_rules.append((False, rule.split(">")[0], int(rule.split(">")[1]), target))
                    else:
                        raise Exception()
                else:
                    if default is not None:
                        raise Exception()
                    default = rule
            if default is None:
                raise Exception()
            if rule_name in ret_rules:
                raise Exception()
            ret_rules[rule_name] = (parsed_rules, default)
        else:
            line = line[1:-1]
            parts.append({k: int(v) for k, v in (x.split("=") for x in line.split(","))})
    return ret_rules, parts


@Task(year=YEAR, day=DAY, task=1)
def task_01(data, log: Callable[[AnyStr], None]):
    rules, parts = data
    log(f"Going to sort {len(parts)} parts using {len(rules)} rules")
    ranges = {}
    for k in set().union(*[x.keys() for x in parts]):
        ranges[k] = (min(x[k] for x in parts), max(x[k] for x in parts))
    ruleset = task(rules=rules, init_ranges=ranges, log=log, start_rule="in", sinks={"A", "R"}, filter_sink="A")
    filtered_parts = [
        x for x in parts if any(all(mi <= x[k] <= ma for k, (mi, ma) in r.items()) for r in ruleset)
    ]
    log(f"{len(filtered_parts)}/{len(parts)} parts match the rules")
    return sum(sum(x.values()) for x in filtered_parts)


@Task(year=YEAR, day=DAY, task=2, extra_config={"raw_ranges": (1, 4000)})
def task_02(data, log: Callable[[AnyStr], None], raw_ranges: Tuple[int, int]):
    rules, parts = data
    ranges = {k: raw_ranges for k in set().union(*[x.keys() for x in parts])}
    log(f"Searching for all distinct combinations of parts that will be accepted.")
    log(f"The values in all parts can range from {raw_ranges[0]} to {raw_ranges[1]}")
    ruleset = task(rules=rules, init_ranges=ranges, log=log, start_rule="in", sinks={"A", "R"}, filter_sink="A")
    ret = 0
    for rule in ruleset:
        ret += prod([x2 - x1 + 1 for x1, x2 in rule.values()])
    log(f"{ret} distinct combinations will be accepted")
    return ret


def task(
        rules: Dict[str, Tuple[List[Tuple[bool, str, int, str]], str]],
        init_ranges: Dict[str, Tuple[int, int]],
        start_rule: str, sinks: Set[str], filter_sink: str,
        log: Callable[[AnyStr], None],
):
    log(f"Starting work in rule <{start_rule}>")
    log(f"Sinking in {', '.join(f'>{x}<' if x == filter_sink else x for x in sorted(sinks))}")

    t1 = perf_counter()
    merged_rules = merge_rules(init_ranges=init_ranges, rules=rules, sinks=sinks, start_rule=start_rule)
    t2 = perf_counter()
    log(f"Rule merging took {t2 - t1:.6f}s")
    log(f"Merged rules. {', '.join(f'{len(v)} rules lead to {k}' for k, v in merged_rules.items())}")
    log(f"Finding all parts that fall into {filter_sink}")
    return merged_rules[filter_sink]



def merge_rules(
        init_ranges: Dict[str, Tuple[int, int]],
        rules: Dict[str, Tuple[List[Tuple[bool, str, int, str]], str]],
        sinks: Set[str],
        start_rule: str,
) -> Dict[str, List[Dict[str, Tuple[int, int]]]]:
    ret: Dict[str, List] = {x: [] for x in sinks}

    current_ranges: List[Tuple[str, Dict[str, Tuple[int, int]]]] = [(start_rule, init_ranges)]

    while len(current_ranges) > 0:
        rule_key, rng = current_ranges.pop()
        rule = rules[rule_key]
        check_rules, default_rule = rule
        for (smaller, k, v, n) in check_rules:
            if rng is None:
                break
            if smaller:
                if rng[k][0] <= v <= rng[k][1]:
                    rng1 = {x: (y[0], v - 1) if x == k else y for x, y in rng.items()}
                    rng2 = {x: (v, y[1]) if x == k else y for x, y in rng.items()}
                elif rng[k][1] < v:
                    rng1 = rng
                    rng2 = None
                else:
                    rng1 = None
                    rng2 = rng
            else:
                if rng[k][0] <= v <= rng[k][1]:
                    rng1 = {x: (v + 1, y[1]) if x == k else y for x, y in rng.items()}
                    rng2 = {x: (y[0], v) if x == k else y for x, y in rng.items()}
                elif rng[k][0] > v:
                    rng1 = rng
                    rng2 = None
                else:
                    rng1 = None
                    rng2 = rng
            if rng1 is not None:
                if n in ret:
                    ret[n].append(rng1)
                else:
                    current_ranges.append((n, rng1))
            rng = rng2
        if rng is not None:
            if default_rule in ret:
                ret[default_rule].append(rng)
            else:
                current_ranges.append((default_rule, rng))

    return ret
