_SPECIAL_SNAFU = {
    "-": -1,
    "=": -2,
}


def _sign(v: int):
    return -1 if v < 0 else 1


def to_snafu(value: int, base: int = 5) -> str:
    if value == 0:
        return ""
    max_fact = base // 2

    j = 0
    while True:
        mult = base ** j
        if abs(value) <= mult * max_fact:
            break
        j += 1

    ret = []
    for _j in range(j, -1, -1):
        mult = base ** _j
        v = sorted(range(-max_fact, max_fact + 1, 1), key=lambda i: abs(value - mult * i))[0]
        value -= mult * v
        ret.append([k for k, _v in _SPECIAL_SNAFU.items() if _v == v][0] if v < 0 else v)

    return "".join(str(x) for x in ret).lstrip("0")


def from_snafu(value: str, base: int = 5) -> int:
    value = value.strip()
    ret = 0
    for i, c in enumerate(reversed(value)):
        fac = _SPECIAL_SNAFU[c] if c in _SPECIAL_SNAFU else int(c)
        mult = base ** i
        ret += fac * mult
    return ret
