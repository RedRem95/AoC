from typing import Dict, Any

import numpy as np


class CRT:
    def __init__(self, w: int, h: int, pixel_type=bool, pixel: Dict[Any, str] = None):
        if pixel is None:
            pixel = {
                True: "#",
                False: ".",
            }
        self._pixel = pixel
        self._crt = np.zeros((h, w), dtype=pixel_type)

    def draw(self, x: int, y: int, value: bool = True):
        self._crt[y, x] = value

    def draw_computer(self, cycle: int, register: np.ndarray, sprite_width: int = 3) -> bool:
        cycle -= 1
        if sprite_width % 2 == 0:
            raise Exception()
        sprite_pos = register[0]
        h, w = self._crt.shape
        cycle = cycle % (h * w)
        y = cycle // w
        x = cycle % w
        if (sprite_pos - (sprite_width // 2)) <= x <= (sprite_pos + (sprite_width // 2)):
            self.draw(x=x, y=y, value=True)
        return True

    def print_screen(self, draw_header: bool = False, draw_box: bool = False) -> str:
        ret = []
        if draw_header:
            ret.append(str(self))
        if draw_box:
            ret.append(f"┏{'━' * self._crt.shape[1]}┓")
            template = "┃{line:%ds}┃" % self._crt.shape[1]
        else:
            template = "{line}"
        for line_idx in range(self._crt.shape[0]):
            line = []
            for col_idx in range(self._crt.shape[1]):
                line.append(self._pixel[self._crt[line_idx, col_idx]][0])
            ret.append(template.format(line="".join(line)))
        if draw_box:
            ret.append(f"┗{'━' * self._crt.shape[1]}┛")
        return "\n".join(ret)

    def __str__(self):
        return f"CRT {self._crt.shape[1]}x{self._crt.shape[0]} with {len(self._pixel)} colors ({self._crt.dtype})"
