from typing import List, Dict, Callable
from collections import Counter, defaultdict

from .CamelCards import Card


def n_of_a_kind(cards: List[Card], n: int) -> List[Card]:

    if n <= 0:
        return []
    if len(cards) < n:
        return []
    if len(cards) == n:
        if all(cards[0] == c for c in cards):
            return [cards[0]]
        return []
    c = Counter(cards)
    return [k for k, v in c.items() if v == n]


# OF_A_KIND: Dict[int, Callable[[List[Card]], bool]] = defaultdict(lambda n: lambda y: len(n_of_a_kind(y, n)) > 0)

def get_of_a_kind_rule(n: int) -> Callable[[List[Card]], bool]:
    def _r(cards: List[Card]) -> bool:
        return len(n_of_a_kind(cards=cards, n=n)) == 1
    return _r


def full_house(cards: List[Card]) -> bool:
    if len(cards) != 5:
        return False
    return len(n_of_a_kind(cards, 3)) == 1 and len(n_of_a_kind(cards, 2)) == 1


def two_pairs(cards: List[Card]) -> bool:
    return len(n_of_a_kind(cards, 2)) == 2


def high_card(cards: List[Card]) -> bool:
    return len(set(cards)) == len(cards)

