import os.path
from functools import lru_cache
from typing import Callable, AnyStr, List

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor

if os.path.basename(os.path.dirname(os.path.dirname(__file__))).startswith("y"):
    _YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[len("y"):])
else:
    raise Exception()

if os.path.basename(os.path.dirname(__file__)).startswith("Day"):
    _DAY = int(os.path.basename(os.path.dirname(__file__))[len("Day"):])
else:
    raise Exception()


def mix(secret_number: int, value: int) -> int:
    return secret_number ^ value


def prune(secret_number: int, value: int = 16777216) -> int:
    return secret_number % value


@lru_cache(maxsize=None)
def step1(secret_number: int, value: int = 64) -> int:
    return prune(secret_number=mix(secret_number=secret_number, value=secret_number * value))


@lru_cache(maxsize=None)
def step2(secret_number: int, value: int = 32) -> int:
    return prune(secret_number=mix(secret_number=secret_number, value=secret_number // value))


def step3(secret_number: int, value: int = 2048) -> int:
    return step1(secret_number=secret_number, value=value)


@lru_cache(maxsize=None)
def next_secret_number(secret_number: int) -> int:
    secret_number = step1(secret_number=secret_number)
    secret_number = step2(secret_number=secret_number)
    secret_number = step3(secret_number=secret_number)
    return secret_number


def get_next_secret_numbers(secret_number: int, amount: int) -> List[int]:
    secret_numbers = [secret_number]
    for _ in range(amount):
        secret_number = next_secret_number(secret_number=secret_number)
        secret_numbers.append(secret_number)
    return secret_numbers


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    return [int(x) for x in data if len(x) > 0]


@Task(year=2024, day=_DAY, task=1, extra_config={"prediction_length": 2000})
def task01(data, log: Callable[[AnyStr], None], prediction_length: int):
    from tqdm import tqdm
    log(f"Predicting the next {prediction_length} secret numbers of {len(data)} monkeys")
    ret = []
    for secret_number in tqdm(data, desc="Predicting secret numbers", leave=False):
        ret.append(get_next_secret_numbers(secret_number=secret_number, amount=prediction_length)[-1])
    r = sum(ret)
    log(f"The sum of the {len(data)} {prediction_length}th secret numbers is {r}")
    return r


@Task(year=2024, day=_DAY, task=2, extra_config={"prediction_length": 2000, "change_sequence_length": 4})
def task02(data, log: Callable[[AnyStr], None], prediction_length: int, change_sequence_length: int):
    from tqdm import tqdm
    price_sequences = []
    log(f"Getting monkey prices for {len(data)} monkeys on {prediction_length} generated prices")
    for secret_number in tqdm(data, desc="Collecting secret numbers", leave=False):
        sequence = get_next_secret_numbers(secret_number=secret_number, amount=prediction_length)
        price_sequences.append([x % 10 for x in sequence])
    log(f"Searching for prices indicated by {change_sequence_length} long change sequences")
    change_sequence_to_price = []
    for sequence in price_sequences:
        prev_changes = tuple()
        change_sequence_to_price.append({})
        for idx, (i, j) in enumerate(zip(sequence, sequence[1:]), 1):
            change = j - i
            prev_changes = prev_changes[-(change_sequence_length - 1):] + (change,)
            if prev_changes not in change_sequence_to_price[-1]:
                change_sequence_to_price[-1][prev_changes] = j
    changes = set().union(*[x.keys() for x in change_sequence_to_price])
    log(f"There are {len(changes)} possible change sequences in the monkey price sequences")
    best_price, best_change = 0, None
    for combination in tqdm(changes, desc="Trying combinations", leave=False):
        price = sum(x.get(combination, 0) for x in change_sequence_to_price)
        if price > best_price:
            best_price = price
            best_change = combination

    log(f"The best price you can get is {best_price} when giving the combination {best_change}")

    return best_price
