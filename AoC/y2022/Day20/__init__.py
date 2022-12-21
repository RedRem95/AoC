from typing import Callable, AnyStr, List

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022, day=20)
def preproc_1(data):
    ret = []
    for line in data:
        line = line.strip()
        if len(line) <= 0:
            continue
        ret.append(int(line))
    return ret


@Task(year=2022, day=20, task=1, extra_config={"start_bit": 0, "offsets": [1000, 2000, 3000]})
def task01(data: List[int], log: Callable[[AnyStr], None], start_bit: int, offsets: List[int]):
    return _run(data=data, log=log, start_bit=start_bit, offsets=offsets, key=1, decrypt_times=1)


@Task(year=2022, day=20, task=2, extra_config={
    "start_bit": 0, "offsets": [1000, 2000, 3000], "key": 811589153, "decrypt_times": 10
})
def task02(data, log: Callable[[AnyStr], None], start_bit: int, offsets: List[int], key: int, decrypt_times: int):
    return _run(data=data, log=log, start_bit=start_bit, offsets=offsets, key=key, decrypt_times=decrypt_times)


def _run(
        data: List[int],
        log: Callable[[AnyStr], None],
        start_bit: int,
        offsets: List[int],
        key: int = 1,
        decrypt_times: int = 1,
):
    log(f"Mixin stream of {len(data)} numbers {decrypt_times} times with key {key}")
    mixed_list = _mix_list(data=data, times=decrypt_times, key=key)
    start_idx = mixed_list.index(start_bit)
    log(f"Start of data is a '{start_bit}' at index {start_idx}")
    log(f"Searching for offset numbers at {', '.join(f'{x}' for x in offsets)}")
    ret = 0
    for offset in offsets:
        search_idx = (start_idx + offset) % len(mixed_list)
        v = mixed_list[search_idx]
        ret += v
        log(f"  Value at offset {offset} is at index {search_idx} => {v}")
    log(f"Sum of important values is {ret}")
    return ret


def _mix_list(data: List[int], times: int = 1, key: int = 1) -> List[int]:
    from collections import deque
    from tqdm import tqdm
    data = [(i, x * key) for i, x in enumerate(data)]
    d = deque(data)

    with tqdm(total=times * len(data), leave=False, desc="Mixing numbers") as pb:
        for _ in range(times):
            for i, num in data:
                pb.update(n=1)
                d.rotate(-d.index((i, num)))
                v = d.popleft()
                d.rotate(-num)
                d.appendleft(v)

    return [x[1] for x in d]
