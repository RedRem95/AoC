import os.path
from collections import Counter
from copy import deepcopy
from time import perf_counter
from typing import Callable, AnyStr, List, Tuple

import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor

from ..Day08 import tpl_add

if os.path.basename(os.path.dirname(os.path.dirname(__file__))).startswith("y"):
    _YEAR = int(os.path.basename(os.path.dirname(os.path.dirname(__file__)))[len("y"):])
else:
    raise Exception()

if os.path.basename(os.path.dirname(__file__)).startswith("Day"):
    _DAY = int(os.path.basename(os.path.dirname(__file__))[len("Day"):])
else:
    raise Exception()


def mult(*args):
    ret = 1
    for n in args:
        ret *= n
    return ret


def wrap_around(pos: Tuple[int, int], bounds: Tuple[Tuple[int, int], Tuple[int, int]]) -> Tuple[int, int]:
    (min_x, max_x), (min_y, max_y) = bounds
    while not (min_x <= pos[0] < max_x):
        if pos[0] < min_x:
            pos = (max_x - abs(pos[0] - min_x), pos[1])
        elif pos[0] >= max_x:
            pos = (min_x + (pos[0] % (max_x - min_x)), pos[1])
    while not (min_y <= pos[1] < max_y):
        if pos[1] < min_y:
            pos = (pos[0], max_y - abs(pos[1] - min_y))
        elif pos[1] >= max_y:
            pos = (pos[0], min_y + (pos[1] % (max_y - min_y)))
    return pos


class Robot:
    def __init__(self, position: Tuple[int, int], velocity: Tuple[int, int]):
        self._position: Tuple[int, int] = position
        self._velocity: Tuple[int, int] = velocity

    @classmethod
    def parse_line(cls, line: str) -> "Robot":
        pos, vel = [x for x in line.strip().split(" ") if len(x) > 0]
        positions = [int(x.strip()) for x in pos.split("=")[-1].split(",")]
        velocities = [int(x.strip()) for x in vel.split("=")[-1].split(",")]
        return cls(position=(positions[0], positions[1]), velocity=(velocities[0], velocities[1]))

    @property
    def position(self) -> Tuple[int, int]:
        return self._position

    @property
    def velocity(self) -> Tuple[int, int]:
        return self._velocity

    def simulate(self, n=1, bounds: Tuple[Tuple[int, int], Tuple[int, int]] = None):
        start_pos, start_vel = self._position, self._velocity
        i = 0
        while i < n:
            self._position = tpl_add(self._position, self.velocity)
            if bounds is not None:
                self._position = wrap_around(pos=self._position, bounds=bounds)
            i += 1
            if self._position == start_pos and self._velocity == start_vel:
                i = n - (n % i)

    def __copy__(self, *args):
        return Robot(position=self.position, velocity=self.velocity)

    def __deepcopy__(self, *args):
        return self.__copy__()


@Preprocessor(year=_YEAR, day=_DAY)
def preproc_1(data):
    ret = []
    for line in (x for x in data if len(x) > 0):
        ret.append(Robot.parse_line(line=line))
    return ret


@Task(year=_YEAR, day=_DAY, task=1, extra_config={"bounds": ((0, 101), (0, 103)), "sim_steps": 100})
def task01(data: List[Robot], log: Callable[[AnyStr], None],
           bounds: Tuple[Tuple[int, int], Tuple[int, int]], sim_steps: int):
    (min_x, max_x), (min_y, max_y) = bounds
    field_width, field_height = max_x - min_x, max_y - min_y
    quad_width, quad_height = field_width // 2, field_height // 2
    log(f"Simulating movement of {len(data)} robots on a {field_width}x{field_height} field for {sim_steps} steps")
    for robot in data:
        robot.simulate(n=sim_steps, bounds=bounds)
    quadrants = {
        0: ((min_x, min_x + quad_width), (min_y, min_y + quad_height)),
        1: ((max_x - quad_width, max_x), (min_y, min_y + quad_height)),
        2: ((min_x, min_x + quad_width), (max_y - quad_height, max_y)),
        3: ((max_x - quad_width, max_x), (max_y - quad_height, max_y)),
    }
    tile_counter = Counter(robot.position for robot in data)
    log(f"After {sim_steps} steps the robots occupy {len(tile_counter)} spaces")
    crowded_place, crowded_count = tile_counter.most_common(1)[0]
    log(f"The most crowded one is at {crowded_place} with {crowded_count} robots")
    quadrant_counter = {k: 0 for k in quadrants.keys()}
    for pos, n in tile_counter.items():
        x, y = pos
        for idx, ((min_x_quad, max_x_quad), (min_y_quad, max_y_quad)) in quadrants.items():
            if min_x_quad <= x < max_x_quad and min_y_quad <= y < max_y_quad:
                quadrant_counter[idx] += n
    ret = mult(*quadrant_counter.values())
    log(f"Checked for robot positions in {len(quadrants)} quadrants. Safety value is {ret}")
    return ret


@Task(year=_YEAR, day=_DAY, task=2, extra_config={"bounds": ((0, 101), (0, 103)), "render": True})
def task02(data: List[Robot], log: Callable[[AnyStr], None],
           bounds: Tuple[Tuple[int, int], Tuple[int, int]], render: bool):
    from tqdm import trange, tqdm
    video_robots = deepcopy(data)

    log(f"Searching for the robot positions that form a christmas tree")
    robot_positions = set()
    sim_steps = 0
    with tqdm(desc="Searching for christmas tree", unit="second", leave=False) as pb:
        t1 = perf_counter()
        while len(robot_positions) != len(data):
            sim_steps += 1
            pb.update(n=1)
            for robot in data:
                robot.simulate(n=1, bounds=bounds)
            robot_positions = set(robot.position for robot in data)
        t2 = perf_counter()
    log(f"Found that the christmas tree shows up after {sim_steps} steps of simulation")
    log(f"Search took {t2 - t1:.4} seconds")
    if render:
        try:
            import imageio as iio
            from PIL import Image
            f_name_video = os.path.join(os.path.dirname(__file__), "p2.mp4")
            f_name_image = os.path.join(os.path.dirname(__file__), "p2_tree.png")
            with iio.get_writer(
                    f_name_video, fps=4, codec="libx264", quality=3, ffmpeg_log_level="quiet", macro_block_size=16
            ) as writer:
                def _draw(heading):
                    img = _draw_frame(robots=video_robots, bounds=bounds, header=heading, pixel=11 * 4)
                    writer.append_data(scale_image(img=np.array(img), scale=1, block_size=16))

                _draw(heading=f"Step: {0}")
                for i in trange(sim_steps, desc="Simulating for render", leave=False, unit="second"):
                    for robot in video_robots:
                        robot.simulate(n=1, bounds=bounds)
                    _draw(heading=f"Step: {i + 1}")
                for _ in range(4 * 10):
                    _draw(heading=f"Step: {i + 1} => The <<CHRISTMAS TREE>>")
                with open(f_name_image, "wb") as f_out:
                    img = _draw_frame(robots=video_robots, bounds=bounds, header=f"<<CHRISTMAS TREE>>", pixel=11 * 4)
                    Image.fromarray(scale_image(img=np.array(img), scale=1, block_size=1)).save(f_out)
                log(f"Rendered video to {os.path.abspath(f_name_video)}")
                log(f"Rendered image to {os.path.abspath(f_name_image)}")
        except ImportError as e:
            log(f"Failed to render video and image cause of missing libraries: {e.name}")
    return sim_steps


def _draw_frame(robots: List[Robot], bounds: Tuple[Tuple[int, int], Tuple[int, int]], header: str, pixel: int = 11):
    from PIL import Image, ImageDraw, ImageFont
    tile_counter = Counter(robot.position for robot in robots)
    (min_x, max_x), (min_y, max_y) = bounds
    field_width, field_height = max_x - min_x, max_y - min_y

    bg = (0, 0, 0)
    heading_color = (127, 131, 134)
    pixel_color = [(205, 28, 54), (57, 90, 50)]

    heading_size = pixel * 4

    ret = Image.new("RGB", ((field_width + 2) * pixel, (field_height + 3) * pixel + heading_size), bg)
    draw = ImageDraw.Draw(ret)

    font = ImageFont.truetype(font="arial.ttf", size=heading_size)
    draw.text((pixel * (field_width / 2 + 0.5), pixel),
              header, heading_color, font, align="center", anchor="mt")

    for x in range(field_width):
        for y in range(field_height):
            pixel_x, pixel_y = (x + 1) * pixel, (y + 2) * pixel + heading_size
            pos = x + min_x, y + min_y
            pos_color = pixel_color[sum(pos) % len(pixel_color)]
            if tile_counter[pos] > 0:
                draw.rectangle(
                    xy=((pixel_x, pixel_y), (pixel_x + pixel, pixel_y + pixel)),
                    fill=pos_color, outline=None, width=0
                )
    return ret


# noinspection DuplicatedCode
def scale_image(img: np.ndarray, scale: int, block_size: int = 1) -> np.ndarray:
    from PIL import Image
    new_size = np.array(list(reversed(img.shape[:2]))) * scale
    new_size = block_size * np.ceil(new_size / block_size).astype(int)
    img = Image.fromarray(img)
    img = img.resize(size=new_size, resample=Image.NEAREST)
    img = np.array(img)
    return img
