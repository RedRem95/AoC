from typing import Callable, AnyStr, List, Tuple, Dict
from copy import deepcopy

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

_stack_type = Dict[int, List[str]]
_command_type = List[Tuple[int, int, int]]


@Preprocessor(year=2022, day=5)
def preproc_1(data):
    _stack_width = 3
    i = 0
    stack: _stack_type = {}
    for i, line in enumerate(data):
        line = line.rstrip()
        j = 0
        while j < len(line):
            idx = j // (_stack_width + 1) + 1
            sliced_line = line[j:j + _stack_width]
            if not all(x == " " for x in sliced_line):
                if idx not in stack:
                    stack[idx] = []
                if str(sliced_line[1]).isalpha():
                    stack[idx].insert(0, sliced_line[1])
            j += _stack_width + 1
        if len(line) <= 0:
            break

    commands: _command_type = []

    for line in data[i + 1:]:
        line = line.strip()
        if len(line) <= 0:
            break
        s = line.split(" ")
        commands.append((int(s[1]), int(s[3]), int(s[5])))

    return stack, commands


# noinspection DuplicatedCode
@Task(year=2022, day=5, task=1)
def task01(data: Tuple[_stack_type, _command_type], log: Callable[[AnyStr], None]):
    stack = deepcopy(data[0])
    commands = deepcopy(data[1])
    log(f"Rearranging {len(stack)} stacks with {sum(len(x) for x in stack.values())} crates using \"CrateMover 9000\"")
    log(f"There are {len(commands)} commands, moving {sum(x[0] for x in commands)} crates")
    log(f"Before rearranging the highest stack has {max(len(x) for x in stack.values())} crates")
    for a, f, t in commands:
        for _ in range(a):
            crane = stack[f].pop(-1)
            stack[t].append(crane)
    log(f"After rearranging the highest stack has {max(len(x) for x in stack.values())} crates")

    ret = []
    for k in sorted(stack.keys()):
        ret.append(stack[k][-1])
    return "".join(ret)


# noinspection DuplicatedCode
@Task(year=2022, day=5, task=2)
def task02(data: Tuple[_stack_type, _command_type], log: Callable[[AnyStr], None]):
    commands = deepcopy(data[1])
    stack = deepcopy(data[0])
    log(f"Rearranging {len(stack)} stacks with {sum(len(x) for x in stack.values())} crates using \"CrateMover 9001\"")
    log(f"There are {len(commands)} commands, moving {sum(x[0] for x in commands)} crates")
    log(f"Before rearranging the highest stack has {max(len(x) for x in stack.values())} crates")
    for a, f, t in commands:
        crane = stack[f][-a:]
        stack[f] = stack[f][:-a]
        stack[t].extend(crane)
    log(f"After rearranging the highest stack has {max(len(x) for x in stack.values())} crates")

    ret = []
    for k in sorted(stack.keys()):
        ret.append(stack[k][-1])

    return "".join(ret)
