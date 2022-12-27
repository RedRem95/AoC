_SPECIAL_SNAFU = {
    "-": -1,
    "=": -2,
}


def to_snafu(value: int, base: int = 5) -> str:
    from sys import maxsize
    if value == 0:
        return ""
    max_fact = base // 2

    def _to_snafu(_value: int, _max_len: int) -> str:
        j = 0
        while True:
            mult = base ** j
            if j >= _max_len or abs(value) <= mult * max_fact:
                for i in range(max_fact, 0, -1):
                    if abs(value) <= mult * (i - 1):
                        continue
                    v = mult * i
                    if value < 0:
                        v_new = value + v
                        print(1, v_new, value, v, mult, i, base, j)
                        return f"{[k for k, v in _SPECIAL_SNAFU.items() if v == -i][0]}{_to_snafu(_value=v_new, _max_len=j-1)}"
                    else:
                        v_new = value - v
                        print(2, v_new, value, v, mult, i, base, j)
                        return f"{i}{_to_snafu(_value=v_new, _max_len=j-1)}"
            j += 1

    return _to_snafu(_value=value, _max_len=maxsize)


def from_snafu(value: str, base: int = 5) -> int:
    value = value.strip()
    ret = 0
    for i, c in enumerate(reversed(value)):
        fac = _SPECIAL_SNAFU[c] if c in _SPECIAL_SNAFU else int(c)
        mult = base ** i
        ret += fac * mult
    return ret
