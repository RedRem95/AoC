from copy import deepcopy
from typing import Optional, List, Tuple, Dict, Set


class SegmentDisplay:
    _digits: Dict[Tuple[str, ...], int] = {
        tuple(sorted("abcefg")): 0,
        tuple(sorted("cf")): 1,
        tuple(sorted("acdeg")): 2,
        tuple(sorted("acdfg")): 3,
        tuple(sorted("bcdf")): 4,
        tuple(sorted("abdfg")): 5,
        tuple(sorted("abdefg")): 6,
        tuple(sorted("acf")): 7,
        tuple(sorted("abcdefg")): 8,
        tuple(sorted("abcdfg")): 9
    }

    @classmethod
    def get_digits(cls) -> Dict[Tuple[str, ...], int]:
        return deepcopy(cls._digits)

    @classmethod
    def get_reversed_digits(cls) -> Dict[int, Tuple[str, ...]]:
        return {v: k for k, v in cls.get_digits().items()}

    def __init__(self, line: Optional[Tuple[List[str], List[str]]] = None):
        if line is not None:
            found_sames: Dict[str, str] = {}
            _: Set[Tuple[str, ...]] = set(tuple(sorted(x)) for x in line[0] + line[1])
            all_numbers: List[Set[str]] = [set(x) for x in _]

            found_digits: Dict[int, Set[str]] = {
                1: [x for x in all_numbers if len(x) == 2][0],
                4: [x for x in all_numbers if len(x) == 4][0],
                7: [x for x in all_numbers if len(x) == 3][0],
                8: [x for x in all_numbers if len(x) == 7][0],
            }

            found_sames["a"] = list(found_digits[7].difference(found_digits[1]))[0]

            find_d = set.intersection(
                *[y for y in [x.difference({found_sames["a"]}) for x in all_numbers] if len(y) == 4])
            found_sames["d"] = list(find_d)[0]

            find_g = set.intersection(*[y for y in all_numbers if len(y) == 5]).difference(set(found_sames.values()))
            found_sames["g"] = list(find_g)[0]

            find_0 = [x for x in all_numbers if len(x) == 6 and len(x.difference(set(found_sames.values()))) == 4][0]
            find_b = set.intersection(find_0, found_digits[4]).difference(found_digits[1])
            found_sames["b"] = list(find_b)[0]

            find_e = set.difference(find_0, set(found_sames.values())).difference(found_digits[1])
            found_sames["e"] = list(find_e)[0]

            find_6 = [x for x in all_numbers if len(x) == 6 and len(x.difference(set(found_sames.values()))) == 1][0]
            find_f = find_6.difference(set(found_sames.values()))
            found_sames["f"] = list(find_f)[0]

            find_c = found_digits[1].difference(find_f)
            found_sames["c"] = list(find_c)[0]

            self._translation_line_to_orig = {v: k for k, v in found_sames.items()}
        else:
            self._translation_line_to_orig = {k: k for k in set.union(*[set(x) for x in self.__class__._digits.keys()])}

    def get_num_from_str(self, num: str) -> int:
        translated = tuple(sorted(self.get_translation_line_to_orig()[x] for x in num))
        return self.get_digits()[translated]

    def parse_line(self, line: Tuple[List[str], ...]) -> Tuple[List[int], ...]:
        return tuple([self.get_num_from_str(x) for x in line_part] for line_part in line)

    def get_translation_orig_to_line(self):
        return {k: v for k, v in self.get_translation_line_to_orig().items()}

    def get_translation_line_to_orig(self):
        return deepcopy(self._translation_line_to_orig)

    @classmethod
    def get_default_translation(cls) -> Dict[str, str]:
        return {k: k for k in set.union(*[set(x) for x in cls.get_digits().keys()])}

    @classmethod
    def get_symbol_map(cls) -> Dict[str, List[Tuple[int, int]]]:
        return {
            "a": [(0, 1), (0, 2), (0, 3), (0, 4)],
            "d": [(3, 1), (3, 2), (3, 3), (3, 4)],
            "g": [(6, 1), (6, 2), (6, 3), (6, 4)],
            "b": [(1, 0), (2, 0)],
            "e": [(4, 0), (5, 0)],
            "c": [(1, 5), (2, 5)],
            "f": [(4, 5), (5, 5)],
        }

    @classmethod
    def to_str(cls, num: int, translation: Dict[str, str] = None, none_symbol: str = ".") -> List[List[str]]:
        if 0 > num or 9 < num:
            raise ValueError("Only values between 0 and 9 are supported")
        if translation is None:
            translation = cls.get_default_translation()
        symbol_map = cls.get_symbol_map()
        num_symbols = cls.get_reversed_digits().get(num, tuple())
        max_w = max(j[1] for i in symbol_map.values() for j in i)
        max_h = max(j[0] for i in symbol_map.values() for j in i)
        ret: List[List[str]] = [[' ' for _ in range((max_w + 1))] for _ in range(max_h + 1)]
        for sym, positions in symbol_map.items():
            if sym in num_symbols:
                sym = translation[sym]
            else:
                sym = none_symbol
            sym = sym[:1]
            for pos_i, pos_j in positions:
                ret[pos_i][pos_j] = sym
        return ret

    @classmethod
    def to_str_multi(cls, nums: List[int], translation: Dict[str, str] = None, none_symbol: str = ".") -> List[
        List[str]]:
        ret = []
        nums = [cls.to_str(num=x) for x in nums]
        for i in range(len(nums[0])):
            line = []
            for num in nums:
                if len(line) > 0:
                    line += [" "]
                line += num[i]
            ret.append(line)
        return ret
