from enum import Enum
from typing import Callable, AnyStr, Tuple, Dict

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


class Outcome(Enum):
    LOSS = 0
    DRAW = 3
    WIN = 6

    def points(self):
        return self.value


class RPS(Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3

    def points(self):
        return self.value

    def wins_against(self) -> "RPS":
        return {
            self.__class__.ROCK: self.__class__.SCISSORS,
            self.__class__.PAPER: self.__class__.ROCK,
            self.__class__.SCISSORS: self.__class__.PAPER,
        }[self]

    def loses_aginst(self) -> "RPS":
        for item in self.__class__:
            if item.wins_against() == self:
                return item
        raise Exception()

    @classmethod
    def outcome(cls, me: "RPS", opponent: "RPS") -> Outcome:
        if me == opponent:
            return Outcome.DRAW
        if me.wins_against() == opponent:
            return Outcome.WIN
        if opponent.wins_against() == me:
            return Outcome.LOSS
        raise Exception()

    def play(self, opponent) -> Tuple[int, Outcome]:
        outcome = self.outcome(me=self, opponent=opponent)
        return self.points() + outcome.points(), outcome

    @classmethod
    def parse(cls, c) -> "RPS":
        return {
            "A": cls.ROCK,
            "B": cls.PAPER,
            "C": cls.SCISSORS,
            "X": cls.ROCK,
            "Y": cls.PAPER,
            "Z": cls.SCISSORS,
        }[c]


@Preprocessor(year=2022, day=2)
def preproc_1(data):
    ret = []
    for line in data:
        line = line.strip()
        if len(line) <= 0:
            continue
        ret.append(tuple(line.split(" ")[:2]))
    return ret


@Task(year=2022, day=2, task=1)
def task01(data, log: Callable[[AnyStr], None]):
    pts = 0
    log(f"You are playing {len(data)} rounds")
    outcomes = {x: 0 for x in Outcome}
    for game in data:
        opponent = RPS.parse(c=game[0])
        me = RPS.parse(c=game[1])
        pt, outcome = me.play(opponent=opponent)
        pts += pt
        outcomes[outcome] += 1
    _summary(outcomes=outcomes, log=log)
    return pts


@Task(year=2022, day=2, task=2)
def task02(data, log: Callable[[AnyStr], None]):
    pts = 0
    conv = {
        "Z": lambda _x: _x.loses_aginst(),
        "Y": lambda _x: _x,
        "X": lambda _x: _x.wins_against()
    }
    log(f"You are playing {len(data)} rounds")
    outcomes = {x: 0 for x in Outcome}
    for game in data:
        opponent = RPS.parse(c=game[0])
        me = conv[game[1]](opponent)
        pt, outcome = me.play(opponent=opponent)
        pts += pt
        outcomes[outcome] += 1
    _summary(outcomes=outcomes, log=log)
    return pts


def _summary(outcomes: Dict[Outcome, int], log: Callable[[AnyStr], None]):
    log(f"Your outcomes:")
    name_len = max(len(x.name) for x in outcomes.keys())
    games_played = sum(x for x in outcomes.values())
    for k in sorted(outcomes.keys(), key=lambda x: x.points()):
        log(f"  {k.name:{name_len}}: {outcomes[k]} ({100 * outcomes[k]/games_played:6.2f}%)")
