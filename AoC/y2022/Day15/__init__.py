import os
from typing import Callable, AnyStr, Tuple, Set, List, Dict

import numpy as np
from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022, day=15)
def preproc_1(data):
    ret = []
    for i in range(len(data)):
        line = data[i]
        line = line.strip()
        if len(line) <= 0:
            continue
        sensor, beacon = line.split(":")
        sensor_x, sensor_y = sensor.split(",")
        sensor_coord = int(sensor_x.split("=")[-1]), int(sensor_y.split("=")[-1])
        beacon_x, beacon_y = beacon.split(",")
        beacon_coord = int(beacon_x.split("=")[-1]), int(beacon_y.split("=")[-1])
        ret.append((sensor_coord, beacon_coord))
    return ret


@Task(year=2022, day=15, task=1, extra_config={"interesting_line": 2000000})
def task01(data, log: Callable[[AnyStr], None], interesting_line: int):
    log(f"There are {len(set(x[0] for x in data))} sensors and {len(set(x[1] for x in data))} beacons")
    log(f"Searching for all points that cant contain a beacon in line {interesting_line}")
    ret = _find_def_not_beacons(x_range=(-np.inf, np.inf), y_range=(interesting_line, interesting_line), data=data)
    log(f"There are {len(ret)} points in line {interesting_line} that cant contain a beacon")
    return len(ret)


@Task(year=2022, day=15, task=2, extra_config={
    "x_range": (0, 4000000), "y_range": (0, 4000000), "draw": False, "max_find": 1
})
def task02(
        data, log: Callable[[AnyStr], None],
        x_range: Tuple[int, int], y_range: Tuple[int, int], max_find: int, draw: bool
):
    log(f"There are {len(set(x[0] for x in data))} sensors and {len(set(x[1] for x in data))} beacons")
    log(f"Searching for {max_find} points that might contain the distress signal that is far away from every sensor")
    log(f"Search is contained in {x_range[0]}-{x_range[1]}x{y_range[0]}-{y_range[1]} area")
    sensors = [(sensor, manhattan_dist(sensor, beacon)) for sensor, beacon in data]
    distress_points = list(_find_distress(sensors=sensors, x_range=x_range, y_range=y_range, max_find=max_find))
    if len(distress_points) != max_find:
        raise Exception()
    log(f"Found {max_find} distress points at {', '.join(str(x) for x in distress_points)}")
    distress_frequencies = [x[0] * 4_000_000 + x[1] for x in distress_points]
    log(f"Distress frequencies of points are {', '.join(str(x) for x in distress_frequencies)}")

    if draw:
        from tqdm import tqdm
        from PIL import Image, ImageDraw

        _COLORS: Dict[int, Tuple[Tuple[int, int, int], int, float]] = {
            0: ((255, 0, 0, 255), 5, 0.1),  # Distress points
            1: ((255, 255, 255), 3, 0.1),  # Sensors
            2: ((0, 0, 255, 255), 3, 0.1),  # Beacon
            3: ((136, 140, 141, 255), 1, 0.0),  # Diamond range
            4: ((0, 255, 0, 255), 1, 0.05),  # Important area
            5: ((0, 0, 0, 255), 1, 1),  # Background
        }

        order = [5, 2, 1, 0, 4, 3]

        x_range = min(x_range), max(x_range)
        y_range = min(y_range), max(y_range)

        print_points_tmp: List[Tuple[int, int, int]] = []
        for x in range(x_range[0], x_range[1] + 1, 1):
            print_points_tmp.append((x, y_range[0], 4))
            print_points_tmp.append((x, y_range[1], 4))
        for y in range(y_range[0], y_range[1] + 1, 1):
            print_points_tmp.append((x_range[0], y, 4))
            print_points_tmp.append((x_range[1], y, 4))
        for sensor, beacon in tqdm(data, desc="Collection points to print", leave=False, unit="s"):
            for diamond_pt in find_diamond(center=sensor, radius=manhattan_dist(sensor, beacon)):
                # print_points_tmp[diamond_pt] = 3
                print_points_tmp.append((diamond_pt[0], diamond_pt[1], 3))
            print_points_tmp.append((sensor[0], sensor[1], 1))
            # print_points_tmp[beacon] = 2
            print_points_tmp.append((beacon[0], beacon[1], 2))
        # print_points_tmp[distress_points[0]] = 4
        for distress_point in distress_points:
            print_points_tmp.append((distress_point[0], distress_point[1], 0))

        print_points = np.array(sorted(print_points_tmp, key=lambda x: order.index(x[-1])))
        del print_points_tmp

        # min_x, max_x = min(x[0] for x in print_points_tmp.keys()), max(x[0] for x in print_points_tmp.keys())
        # min_y, max_y = min(x[1] for x in print_points_tmp.keys()), max(x[1] for x in print_points_tmp.keys())
        min_x, min_y, _ = np.min(print_points, axis=0)
        max_x, max_y, _ = np.max(print_points, axis=0)

        width, height = max_x - min_x, max_y - min_y
        scale = 1
        if width > 4000:
            scale = width / 4000
        width, height = int(width // scale), int(height // scale)

        img = Image.new("RGBA", (width + 1, height + 1), _COLORS[5][0])
        draw = ImageDraw.Draw(img)
        draw: ImageDraw.ImageDraw
        for i in tqdm(range(print_points.shape[0]), total=print_points.shape[0], leave=False, desc="Draw points"):
            x, y, color = print_points[i]
            x -= min_x
            y -= min_y
            x = int(x // scale)
            y = int(y // scale)
            rgb_color, cross_size, factor = _COLORS[color]
            pixel_width = max(0, int(width * (factor / 100)))
            draw.rectangle(
                xy=(x - (pixel_width * cross_size), y - pixel_width, x + (pixel_width * cross_size), y + pixel_width),
                fill=rgb_color,
                outline=rgb_color,
                width=1,
            )
            draw.rectangle(
                xy=(x - pixel_width, y - (pixel_width * cross_size), x + pixel_width, y + (pixel_width * cross_size)),
                fill=rgb_color,
                outline=rgb_color,
                width=1,
            )
            # img.putpixel((x, y), rgb_color)

        img = img.resize((4000, int(4000 * height / width)), Image.NEAREST)

        img.save(os.path.join(os.path.dirname(__file__), "distress_map.png"))

    return distress_frequencies[0]


def manhattan_dist(x1: Tuple[int, ...], x2: Tuple[int, ...]) -> int:
    if len(x1) != len(x2):
        raise Exception()
    return sum(abs(_x1 - _x2) for _x1, _x2 in zip(x1, x2))


def find_diamond(center: Tuple[int, int], radius: int) -> Set[Tuple[int, int]]:
    radius = abs(radius)
    ret = set()
    for y in range(0, radius + 1, 1):
        x = radius - y
        ret.update((
            _tpl_add(center, (-x, -y)),
            _tpl_add(center, (x, -y)),
            _tpl_add(center, (-x, y)),
            _tpl_add(center, (x, y)),
        ))
    return ret


def _tpl_add(t1: Tuple[int, int], t2: Tuple[int, int]) -> Tuple[int, int]:
    return t1[0] + t2[0], t1[1] + t2[1]


def _find_def_not_beacons(
        x_range: Tuple[int, int], y_range: Tuple[int, int], data: List[Tuple[Tuple[int, int], Tuple[int, int]]]
) -> Set[Tuple[int, int]]:
    ret: Set[Tuple[int, int]] = set()

    x_range = min(x_range), max(x_range)

    for sensor, closest_beacon in data:
        sensor_dist = manhattan_dist(sensor, closest_beacon)
        for y in range(min(y_range), max(y_range) + 1, 1):
            x = 0
            left, right = True, True

            while left or right:
                if left:
                    test_pt = (sensor[0] - x, y)
                    if x_range[0] <= test_pt[0] <= x_range[1] and manhattan_dist(test_pt, sensor) <= sensor_dist:
                        ret.add(test_pt)
                    else:
                        left = False
                if right:
                    test_pt = (sensor[0] + x, y)
                    if x_range[0] <= test_pt[0] <= x_range[1] and manhattan_dist(test_pt, sensor) <= sensor_dist:
                        ret.add(test_pt)
                    else:
                        right = False
                x += 1

    ret.difference_update([x[1] for x in data])
    return ret


def _find_distress(
        sensors: List[Tuple[Tuple[int, int], int]], x_range: Tuple[int, int], y_range: Tuple[int, int], max_find: int
) -> Set[Tuple[int, int]]:
    distress_points: Set[Tuple[int, int]] = set()

    x_range = min(x_range), max(x_range)
    y_range = min(y_range), max(y_range)
    x = 1

    while True:
        found = False
        for test_points in (find_diamond(center=c, radius=d + x) for c, d in sensors):
            for test_pt in (x for x in test_points if _check_in_range(x, ranges=[x_range, y_range])):
                found = True
                if all(manhattan_dist(ts, test_pt) > tr for ts, tr in sensors):
                    distress_points.add(test_pt)
                if len(distress_points) >= max_find:
                    return distress_points
        if not found:
            break
        x += 1

    return distress_points


def _check_in_range(pt: Tuple[int, ...], ranges: List[Tuple[int, int]]) -> bool:
    if len(pt) != len(ranges):
        raise Exception()
    return all(r[0] <= x <= r[1] for x, r in zip(pt, ranges))
