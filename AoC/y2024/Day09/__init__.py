import os.path
from typing import Callable, AnyStr, List, Tuple

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor
from tqdm import trange

if os.path.basename(os.path.dirname(__file__)).startswith("Day"):
    _DAY = int(os.path.basename(os.path.dirname(__file__))[len("Day"):])
else:
    raise Exception()


@Preprocessor(year=2024, day=_DAY)
def preproc_1(data):
    data = [x for x in data if len(x) > 0][0]
    files, free = [], []
    for i in range(0, len(data), 2):
        files.append((i // 2, int(data[i])))
        if i + 1 < len(data):
            free.append(int(data[i + 1]))
    return files, free


@Task(year=2024, day=_DAY, task=1)
def task01(data: Tuple[List[Tuple[int, int]], List[int]], log: Callable[[AnyStr], None]):
    files, free = data
    log(f"Trying to optimize {len(files)} files into {len(free)} free spaces.")
    log(f"Disk has {sum(x[1] for x in files) + sum(free)} blocks")
    i, j = 0, 0
    while i < len(free):
        if files[-1][1] <= 0:
            break
        j += 1
        if files[-1][1] > free[i]:
            f_id, f_num = files[-1]
            files[-1] = (f_id, f_num - free[i])
            files.insert(j, (f_id, free[i]))
            free[i] = 0
        elif files[-1][1] <= free[i]:
            f_id, f_num = files.pop(-1)
            files.insert(j, (f_id, f_num))
            free[i] = free[i] - f_num
        else:
            raise Exception()
        if free[i] <= 0:
            i += 1
            j += 1
    # files = [(f_id, f_num) for f_id, f_num in files if f_num > 0]
    ret = 0
    running_sum, j = 0, 0
    for i in trange(sum(x[1] for x in files), desc="Calculating checksum", leave=False):
        while i >= running_sum + files[j][1]:
            running_sum += files[j][1]
            j += 1
        ret += i * files[j][0]
    log(f"Filesystem checksum is {ret}")
    return ret


@Task(year=2024, day=_DAY, task=2)
def task02(data: Tuple[List[Tuple[int, int]], List[int]], log: Callable[[AnyStr], None]):
    files, free = data
    disk = []
    for i in range(len(files)):
        disk.append(files[i])
        if i < len(free):
            disk.append((-1, free[i]))

    log(f"Trying to optimize {len(files)} files into {len(free)} free spaces.")
    log(f"Joined disk has {sum(x[1] for x in disk)} blocks")
    del files, free

    pt_free = 0

    while pt_free < len(disk):
        while disk[pt_free][0] >= 0 or disk[pt_free][1] <= 0:
            pt_free += 1
        pt_full = len(disk) - 1
        while True:
            if pt_full <= pt_free:
                pt_free += 1
                break
            if disk[pt_full][0] >= 0 and (0 < disk[pt_full][1] <= disk[pt_free][1]):
                disk[pt_free] = (-1, disk[pt_free][1] - disk[pt_full][1])
                disk.insert(pt_free, disk[pt_full])
                disk[pt_full + 1] = (-1, disk[pt_full + 1][1])
                pt_free += 1
                break
            pt_full -= 1

    # files = [(f_id, f_num) for f_id, f_num in files if f_num > 0]
    ret = 0
    running_sum, j = 0, 0
    for i in trange(sum(x[1] for x in disk), desc="Calculating checksum", leave=False):
        while i >= running_sum + disk[j][1]:
            running_sum += disk[j][1]
            j += 1
        ret += i * disk[j][0] if disk[j][0] > 0 else 0

    log(f"Filesystem checksum is {ret}")

    return ret
