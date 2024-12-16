import os.path
from collections import defaultdict
from enum import Enum
from functools import lru_cache
from math import ceil
from typing import Callable, AnyStr, List, Tuple, Dict
from uuid import uuid4

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor


def tpl_fn(t1: Tuple[int, ...], t2: Tuple[int, ...], fn: Callable[[int, int], int]) -> Tuple[int, ...]:
    return tuple(fn(i, j) for i, j in zip(t1, t2))


def tpl_add(t1: Tuple[int, ...], t2: Tuple[int, ...]): return tpl_fn(t1, t2, lambda x, y: x + y)


def tpl_mult(t1: Tuple[int, ...], t2: Tuple[int, ...]): return tpl_fn(t1, t2, lambda x, y: x * y)


if os.path.basename(os.path.dirname(os.path.dirname(__file__))).startswith("y"):
    _YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[len("y"):])
else:
    raise Exception()

if os.path.basename(os.path.dirname(__file__)).startswith("Day"):
    _DAY = int(os.path.basename(os.path.dirname(__file__))[len("Day"):])
else:
    raise Exception()


class MapElementStyle(Enum):
    WALL = "#"
    BOX = "O"
    ROBOT = "@"
    NOTHING = "."


movements = {
    "^": (-1, 0),
    "<": (0, -1),
    "v": (1, 0),
    ">": (0, 1),
}

movements_symbol = {
    "^": "↑",
    "<": "←",
    "v": "↓",
    ">": "→",
}

WAREHOUSE_TYPE = Dict[Tuple[int, int], MapElementStyle]
COMMANDS_TYPE = List[str]


@Preprocessor(year=_YEAR, day=_DAY)
def preproc_1(data):
    warehouse = {}
    commands = []
    in_movements = False
    i = 0
    for line in (x.strip() for x in data):
        if len(line) <= 0:
            if len(warehouse) > 0:
                in_movements = True
            continue
        if in_movements:
            commands.extend([str(x) for x in line])
        else:
            for j, el in enumerate(line):
                warehouse[(i, j)] = MapElementStyle(el)
            i += 1
    return warehouse, commands


def run(
        warehouse: WAREHOUSE_TYPE, commands: COMMANDS_TYPE, log: Callable[[AnyStr], None], scale: int,
        render: str = None, video_final_hold_seconds: int = 3, video_commands_per_second: int = 30
) -> int:
    from tqdm import tqdm
    from .video_renderer import VideoRenderer
    scaled_warehouse = Warehouse(warehouse, width_scale=scale)
    with VideoRenderer(fps=video_commands_per_second * 2, log=log, f_name=render, final_as_img=True) as renderer:
        width, height = scaled_warehouse.get_size()
        log(f"Simulating a {width}x{height} warehouse for {len(commands)} commands")
        for i, command in tqdm(enumerate(commands), total=len(commands), leave=False, desc="Executing commands",
                               unit="commands"):
            header = f"Command {i + 1:{len(str(len(commands)))}}: {movements_symbol.get(command, command)}"
            renderer.add_frame(frame=scaled_warehouse.draw_frame(pixel_size=12, header=header), scale=1, )
            scaled_warehouse.step(vel=movements[command])
            renderer.add_frame(frame=scaled_warehouse.draw_frame(pixel_size=12, header=header), scale=1, )
        final_frame = scaled_warehouse.draw_frame(pixel_size=12, header=f"Final warehouse layout")
        for _ in range(video_commands_per_second * 2 * video_final_hold_seconds):
            renderer.add_frame(
                frame=final_frame,
                scale=1,
            )
    boxes = [pos for el, pos in scaled_warehouse.get_elements().items() if el.style == MapElementStyle.BOX]
    log(f"There are {len(boxes)} boxes")
    ret = sum(min(x[0] for x in positions) * 100 + min(x[1] for x in positions) for positions in boxes)
    log(f"sum of GPS coordinates of the boxes is {ret} ")
    return ret


@Task(year=_YEAR, day=_DAY, task=1, extra_config={"render": False})
def task01(data, log: Callable[[AnyStr], None], render: bool):
    return run(
        warehouse=data[0], commands=data[1], log=log, scale=1,
        render=os.path.join(os.path.dirname(__file__), "p1.mp4") if render else None
    )


@Task(year=_YEAR, day=_DAY, task=2, extra_config={"render": False, "warehouse_scale": 2})
def task02(data, log: Callable[[AnyStr], None], render: bool, warehouse_scale: int):
    return run(
        warehouse=data[0], commands=data[1], log=log, scale=warehouse_scale,
        render=os.path.join(os.path.dirname(__file__), "p2.mp4") if render else None
    )


class MapElement:
    def __init__(self, style: MapElementStyle):
        self._style = style
        self._id = uuid4()

    @property
    def style(self) -> MapElementStyle:
        return self._style

    def __eq__(self, other):
        if isinstance(other, MapElement) and self._id == other._id:
            return True
        return False

    def __hash__(self):
        return hash(self._id)

    def __str__(self):
        return self._style.value

    def __repr__(self):
        return f"{self.__class__.__name__}({self._style.value}, {self._id})"

    def __copy__(self) -> "MapElement":
        ret = MapElement(self.style)
        ret._id = self._id
        return ret


class Warehouse:
    def __init__(self, warehouse: WAREHOUSE_TYPE, width_scale: int = 1):
        self._warehouse: Dict[Tuple[int, int], MapElement] = defaultdict(lambda: MapElement(MapElementStyle.NOTHING))
        for line in range(min(x[0] for x in warehouse.keys()), max(x[0] for x in warehouse.keys()) + 1):
            for col in range(min(x[1] for x in warehouse.keys()), max(x[1] for x in warehouse.keys()) + 1):
                map_element = MapElement(style=MapElementStyle(warehouse[(line, col)]))
                for i in range(width_scale):
                    if map_element.style == MapElementStyle.ROBOT and i > 0:
                        map_element = MapElement(style=MapElementStyle.NOTHING)
                    if map_element.style == MapElementStyle.NOTHING:
                        map_element = MapElement(style=MapElementStyle.NOTHING)
                    self._warehouse[(line * 1, col * width_scale + i)] = map_element

    def get_bounds(self):
        width = min(x[1] for x in self._warehouse.keys()), max(x[1] for x in self._warehouse.keys())
        height = min(x[0] for x in self._warehouse.keys()), max(x[0] for x in self._warehouse.keys())
        return width, height

    def get_size(self):
        width, height = self.get_bounds()
        return width[1] - width[0] + 1, height[1] - height[0] + 1

    def __str__(self):
        ret = []
        width, height = self.get_bounds()
        for line in range(height[0], height[1] + 1):
            tmp = []
            for col in range(width[0], width[1] + 1):
                el = self._warehouse.get((line, col), MapElement(style=MapElementStyle.NOTHING))
                if el.style == MapElementStyle.BOX:
                    tmp.append("░")
                elif el.style == MapElementStyle.WALL:
                    tmp.append("▒")
                elif el.style == MapElementStyle.NOTHING:
                    tmp.append(" ")
                else:
                    tmp.append(f"{str(el):1}"[0])
            ret.append("".join(tmp))
        return "\n".join(ret)

    def step(self, vel: Tuple[int, int]):
        robots = [pos for pos, el in self._warehouse.items() if el.style == MapElementStyle.ROBOT]
        if len(robots) != 1:
            raise Exception(f"There has to be exactly one robot in warehouse. {len(robots)} found.")
        robot_pos = robots[0]
        move_commands = self._pot_move(pos=robot_pos, vel=vel)
        if len(move_commands) <= 0:
            return
        solved = set()
        while any(x not in solved for x in move_commands.values()):
            solved_prev = len(solved)
            for target in (x for x in move_commands.values() if x not in solved):
                if self._warehouse[target].style == MapElementStyle.NOTHING:
                    solved.add(target)
                if target in move_commands and move_commands[target] in solved:
                    solved.add(target)
            if len(solved) <= solved_prev:
                return
        tmp_storage = {k: self._warehouse[k] for k in move_commands.keys()}
        for k, el in sorted(tmp_storage.items(), key=lambda k: tpl_mult(k[0], vel), reverse=True):
            self._warehouse[move_commands[k]] = el
            del self._warehouse[k]

    def _pot_move(self, pos: Tuple[int, int], vel: Tuple[int, int]) -> Dict[Tuple[int, int], Tuple[int, int]]:
        if self._warehouse[pos].style in (MapElementStyle.NOTHING, MapElementStyle.WALL):
            return {}
        mes = [p for p, el in self._warehouse.items() if el == self._warehouse[pos]]
        need_move_to = {}
        for me in mes:
            me_next = tpl_add(me, vel)
            need_move_to[me] = me_next
            if me_next in mes:
                continue
            also_need_move_to = self._pot_move(pos=me_next, vel=vel)
            for p, pn in also_need_move_to.items():
                need_move_to[p] = pn
        return need_move_to

    def get_elements(self) -> Dict[MapElement, List[Tuple[int, int]]]:
        ret = defaultdict(list)
        for pos, el in self._warehouse.items():
            ret[el].append(pos)
        return ret

    def draw_frame(self, pixel_size: int, header: str):
        from PIL import Image, ImageDraw, ImageFont
        header = "" if header is None else header
        bg = (0, 0, 0)
        heading_color = (127, 131, 134)

        def pixel_color(_element: MapElement):
            match _element.style:
                case MapElementStyle.BOX:
                    return 205, 28, 54
                case MapElementStyle.WALL:
                    return heading_color
                case MapElementStyle.NOTHING:
                    return None
                case MapElementStyle.ROBOT:
                    return 57, 90, 50
            raise Exception()

        heading_size = pixel_size * 2 if len(header) > 0 else 0

        (y_min, y_max), (x_min, x_max) = self.get_bounds()
        width, height = self.get_size()

        ret = Image.new("RGB", ((width + 2) * pixel_size, (height + 3) * pixel_size + heading_size), bg)
        draw = ImageDraw.Draw(ret)

        font = ImageFont.truetype(font="cour.ttf", size=heading_size)
        if heading_size > 0:
            draw.text((pixel_size * (width / 2 + 0.5), pixel_size),
                      header, heading_color, font, align="center", anchor="mt")

        for x in range(width):
            for y in range(height):
                pixel_x, pixel_y = (x + 1) * pixel_size, (y + 2) * pixel_size + heading_size
                pos = y + y_min, x + x_min
                el = self._warehouse.get(pos, MapElement(style=MapElementStyle.NOTHING))
                pos_color = pixel_color(el)
                if pos_color is not None:
                    self._draw_element(draw=draw, pos=pos, color=pos_color,
                                       xy=((pixel_x, pixel_y), (pixel_x + pixel_size, pixel_y + pixel_size))
                                       )
        return ret

    def _draw_element(self, draw, pos: Tuple[int, int], xy: Tuple[Tuple[int, int], Tuple[int, int]], color):
        from PIL import ImageDraw
        draw: ImageDraw
        nothing = MapElement(style=MapElementStyle.NOTHING)
        el = self._warehouse.get(pos, nothing)
        if el.style == MapElementStyle.NOTHING:
            return
        if el.style == MapElementStyle.ROBOT:
            draw.rectangle(xy=xy, fill=color, outline=None, width=0)
            return
        if el.style in (MapElementStyle.WALL, MapElementStyle.BOX):
            neighbors: List[MapElement] = [
                self._warehouse.get(tpl_add(pos, delta), nothing) for delta in
                [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
            ]
            if el.style == MapElementStyle.WALL:
                friends = [x.style == MapElementStyle.WALL for x in neighbors]
            elif el.style == MapElementStyle.BOX:
                friends = [x == el for x in neighbors]
            else:
                raise Exception()
            (x_min, y_min), (x_max, y_max) = xy
            left_third, right_third, upper_third, lower_third = self.get_fraction(xy, 4)
            n, ne, e, se, s, sw, w, nw = friends
            if not n:
                draw.rectangle(xy=(x_min, y_min, x_max, upper_third), fill=color, outline=None, width=0)
            if not ne and n and e:
                draw.rectangle(xy=(right_third, y_min, x_max, upper_third), fill=color, outline=None, width=0)
            if not e:
                draw.rectangle(xy=(right_third, y_min, x_max, y_max), fill=color, outline=None, width=0)
            if not se and s and e:
                draw.rectangle(xy=(right_third, lower_third, x_max, y_max), fill=color, outline=None, width=0)
            if not s:
                draw.rectangle(xy=(x_min, lower_third, x_max, y_max), fill=color, outline=None, width=0)
            if not sw and s and w:
                draw.rectangle(xy=(x_min, lower_third, left_third, y_max), fill=color, outline=None, width=0)
            if not w:
                draw.rectangle(xy=(x_min, y_min, left_third, y_max), fill=color, outline=None, width=0)
            if not nw and n and w:
                draw.rectangle(xy=(x_min, y_min, left_third, upper_third), fill=color, outline=None, width=0)
            return
        raise Exception()

    @staticmethod
    @lru_cache(maxsize=None)
    def get_fraction(xy, fraction: int = 3):
        (x_min, y_min), (x_max, y_max) = xy
        left_third = x_min + ceil((x_max - x_min) / fraction)
        right_third = x_max - (left_third - x_min)
        upper_third = y_min + ceil((y_max - y_min) / fraction)
        lower_third = y_max - (upper_third - y_min)
        return left_third, right_third, upper_third, lower_third
