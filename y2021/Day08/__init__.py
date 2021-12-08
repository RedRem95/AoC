from typing import Any, Optional, List, Tuple

from AoC_Companion.Day import Day, TaskResult

from .segment_display import SegmentDisplay


class Day08(Day):

    def __init__(self, year: int):
        super().__init__(year)

    def pre_process_input(self, data: Any) -> Any:
        data: List[str] = super().pre_process_input(data=data)
        ret: List[Tuple[List[str], List[str]]] = []
        for line in (d for d in data if len(d) > 0):
            d1, d2 = line.split("|")
            ret.append((d1.strip().split(" "), d2.strip().split(" ")))
        return ret

    def run_t1(self, data: List[Tuple[List[str], List[str]]]) -> Optional[TaskResult]:
        length_counter = {}
        for k in SegmentDisplay.get_digits():
            l_k = len(k)
            if l_k not in length_counter:
                length_counter[l_k] = 0
            length_counter[l_k] += 1
        search = [k for k, v in length_counter.items() if v == 1]
        conv = [[1 if len(y) in search else 0 for y in x[1]] for x in data]
        ret = sum([sum(x) for x in conv])
        log = [
            f"There are {len(data)} lines of segment data",
            f"Searching for unique segment patterns of "
            f"{', '.join(str(x) for x in (k for v, k in SegmentDisplay.get_digits().items() if len(v) in search))}",
            f"Found {ret} instances of interesting patterns"
        ]
        log.extend(
            ["Result:"] + ["".join(x) for x in SegmentDisplay.to_str_multi(nums=[int(x) for x in str(ret)])]
        )
        return TaskResult(ret, log=log)

    def run_t2(self, data: List[Tuple[List[str], List[str]]]) -> Optional[TaskResult]:
        ret = []
        for line in data:
            segment = SegmentDisplay(line=line)
            data = segment.parse_line(line=line)[1]
            value = int("".join(str(x) for x in data))
            ret.append(value)
        ret = sum(ret)
        log = [
            f"There are {len(data)} lines of segment data",
            f"The output of all lines result in a sum of {ret}"
        ]
        log.extend(
            ["Result:"] + ["".join(x) for x in SegmentDisplay.to_str_multi(nums=[int(x) for x in str(ret)])]
        )
        return TaskResult(ret, log=log)
