from typing import Tuple, Optional


def replace_in_tpl(tpl: Tuple, val, idx: int) -> Tuple:
    return *tpl[:idx], val, *tpl[idx + 1:]


def combo_operator(operand: int, register: Tuple[int, ...]) -> int:
    if 0 <= operand <= 3:
        return operand
    if 4 <= operand < 4 + len(register):
        return register[operand - 4]
    raise Exception(f"operand {operand} not supported for combo operator")


def _dv(tar_idx: int, pos: int, operand: int, register: Tuple[int, ...]) -> Tuple[Tuple[int, ...], int, Optional[int]]:
    operand = combo_operator(operand, register)
    val = register[0] // (2 ** operand)
    register = replace_in_tpl(tpl=register, val=val, idx=tar_idx)
    return register, pos + 2, None


def adv(pos: int, operand: int, register: Tuple[int, ...]) -> Tuple[Tuple[int, ...], int, Optional[int]]:
    return _dv(0, pos, operand, register)


def bdv(pos: int, operand: int, register: Tuple[int, ...]) -> Tuple[Tuple[int, ...], int, Optional[int]]:
    return _dv(1, pos, operand, register)


def cdv(pos: int, operand: int, register: Tuple[int, ...]) -> Tuple[Tuple[int, ...], int, Optional[int]]:
    return _dv(2, pos, operand, register)


def bst(pos: int, operand: int, register: Tuple[int, ...]) -> Tuple[Tuple[int, ...], int, Optional[int]]:
    operand = combo_operator(operand, register)
    val = operand % 8
    register = replace_in_tpl(tpl=register, val=val, idx=1)
    return register, pos + 2, None


def jnz(pos: int, operand: int, register: Tuple[int, ...]) -> Tuple[Tuple[int, ...], int, Optional[int]]:
    return register, pos + 2 if register[0] == 0 else operand, None


def out(pos: int, operand: int, register: Tuple[int, ...]) -> Tuple[Tuple[int, ...], int, Optional[int]]:
    val = combo_operator(operand, register)
    return register, pos + 2, val % 8


def bxc(pos: int, operand: int, register: Tuple[int, ...]) -> Tuple[Tuple[int, ...], int, Optional[int]]:
    val = register[1] ^ register[2]
    register = replace_in_tpl(tpl=register, val=val, idx=1)
    return register, pos + 2, None


def bxl(pos: int, operand: int, register: Tuple[int, ...]) -> Tuple[Tuple[int, ...], int, Optional[int]]:
    val = register[1] ^ operand
    register = replace_in_tpl(tpl=register, val=val, idx=1)
    return register, pos + 2, None
