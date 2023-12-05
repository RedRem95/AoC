from typing import Callable, AnyStr, Optional, Dict, List, Tuple
from collections import defaultdict
from time import perf_counter
from itertools import chain

import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2023, day=4)
def preproc_1(data):
    ret = {}
    for line in (x.strip() for x in data if len(x.strip()) > 0):
        card, line = line.split(":")
        card = int([x.strip() for x in card.split(" ") if len(x.strip()) > 0][-1])
        winning, got = line.split("|")
        winning = [int(x.strip()) for x in winning.split(" ") if len(x.strip()) > 0]
        got = [int(x.strip()) for x in got.split(" ") if len(x.strip()) > 0]
        if card in ret:
            raise Exception()
        ret[card] = (winning, got)
    return ret


@Task(year=2023, day=4, task=1)
def task01(data: Dict[int, Tuple[List[int], List[int]]], log: Callable[[AnyStr], None]):
    log(f"Processing {len(data)} cards")
    p = 0
    for card_winning, card_got in data.values():
        same = set(card_winning).intersection(card_got)
        if len(same) > 0:
            p += 2 ** (len(same) - 1)
    log(f"From exp2 rule you got {p} points from {len(data)} cards")
    return p


@Task(year=2023, day=4, task=2)
def task02(data: Dict[int, Tuple[List[int], List[int]]], log: Callable[[AnyStr], None]):
    log(f"Processing {len(data)} cards")
    card_counts = {x: 1 for x in range(min(data.keys()), max(data.keys()) + 1, 1)}
    if any(k not in data for k in card_counts.keys()):
        raise Exception()
    for card_id in sorted(card_counts.keys()):
        card_winning, card_got = data[card_id]
        same = set(card_winning).intersection(card_got)
        winnings = len(same)
        for k in range(card_id + 1, card_id + 1 + winnings):
            if k in card_counts:
                card_counts[k] += card_counts[card_id]
    log(f"Processed {len(data)} cards")
    most_common = sorted(card_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
    log(f"Most common card you got is {most_common[0][0]} with {most_common[0][1]} instances")
    s = sum(card_counts.values())
    log(f"Ultimately you have {s} cards in one big pile. Lol")
    return s
