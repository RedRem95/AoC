from typing import List, Dict, Callable, Iterator
from collections import OrderedDict


class Card:

    _CARDS = {
        True: ["A", "K", "Q", "T", "9", "8", "7", "6", "5", "4", "3", "2", "J"],
        False: ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
    }

    def __init__(self, sym: str, joker_rule: bool):
        if sym not in self.__class__._CARDS[joker_rule]:
            raise Exception(f"{sym} not a valid card ({', '.join(self.__class__._CARDS[joker_rule])})")
        self._sym = sym
        self._strength = self.__class__._CARDS[joker_rule].index(sym)
        self._joker_rule = joker_rule

    def get_sym(self) -> str:
        return self._sym

    def is_joker_rule(self) -> bool:
        return self._joker_rule

    def is_joker(self) -> bool:
        return self.is_joker_rule() and self.get_sym() == "J"

    def iter_non_joker(self) -> Iterator["Card"]:
        if self.is_joker_rule():
            for c in self.__class__._CARDS[self.is_joker_rule()]:
                if c != "J":
                    yield Card(c, False)

    def __str__(self):
        return self.get_sym()

    def __hash__(self):
        return hash(self.get_sym())

    def __eq__(self, __o):
        if isinstance(__o, self.__class__):
            if self.is_joker() or __o.is_joker():
                return __o.get_sym() == self.get_sym()
            return __o.get_sym() == self.get_sym()
        return False

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return other._strength < self._strength


class Hand:

    from .CamelCardRules import full_house, get_of_a_kind_rule, two_pairs, high_card

    _RULES: Dict[str, Callable[[List[Card]], bool]] = OrderedDict([
        ("Five of a kind", get_of_a_kind_rule(5)),
        ("Four of a kind", get_of_a_kind_rule(4)),
        ("Full house", full_house),
        ("Three of a kind", get_of_a_kind_rule(3)),
        ("Two pairs", two_pairs),
        ("Two of a kind", get_of_a_kind_rule(2)),
        ("High card", high_card)
    ])

    _RULES_IDX = list(_RULES.keys())

    def __init__(self, cards: List[Card]):
        self._cards = cards
        self._rule = None
        card_pile = list(self.__class__.generate_card_pile(cards=cards))
        for r_name, r in self.__class__._RULES.items():
            if any(r(c) for c in card_pile):
                self._rule = r_name
                break
        if self._rule is None:
            raise Exception(f"Hand of {', '.join(str(x) for x in cards)} has no applicable rule")
        self._rule_strength = self.__class__._RULES_IDX.index(self._rule)

    def has_joker_rule(self):
        return any(x.is_joker_rule() for x in self._cards)

    def joker_count(self):
        return len([c for c in self._cards if c.is_joker()])

    def __str__(self):
        return f'{", ".join(str(x) for x in self._cards)} ({self._rule})'

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return len(self._cards) == len(other._cards) and all(x1 == x2 for x1, x2 in zip(self._cards, other._cards))
        return False

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            if self._rule_strength == other._rule_strength:
                for i in range(min(len(self._cards), len(other._cards))):
                    if self._cards[i] != other._cards[i]:
                        return self._cards[i] < other._cards[i]
            return other._rule_strength < self._rule_strength

    @classmethod
    def generate_card_pile(cls, cards: List[Card]) -> Iterator[List[Card]]:
        r = []
        for i, c in enumerate(cards):
            if c.is_joker():
                for pc in c.iter_non_joker():
                    for rest in cls.generate_card_pile(cards[i+1:]):
                        yield r + [pc] + rest
                return
            else:
                r.append(c)
        yield r

