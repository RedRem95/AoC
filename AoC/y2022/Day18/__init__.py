from dataclasses import dataclass
from functools import total_ordering
from typing import Callable, AnyStr, List, Tuple, Set, Dict

from AoC_Companion.Day import Task
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022, day=18)
def preproc_1(data):
    ret = []
    for line in data:
        line = line.strip()
        if len(line) <= 0:
            continue
        x, y, z = line.split(",")
        cube = Cube(x=int(x), y=int(y), z=int(z))
        ret.append(cube)
    return ret


@Task(year=2022, day=18, task=1)
def task01(data: List["Cube"], log: Callable[[AnyStr], None]):
    log(f"There are {len(data)} cubes")
    outside_faces: Dict[int, Tuple[Face, bool]] = dict()
    face_count = 0
    for cube in data:
        for face in cube.get_faces():
            face_count += 1
            c_face = hash(face)
            if c_face in outside_faces:
                outside_faces[c_face] = (face, False)
            else:
                outside_faces[c_face] = (face, True)
    ret = sum(1 for k in outside_faces.values() if k[1])
    log(f"There are {face_count} faces. {ret} facing outwards {face_count - ret} inwards")
    return ret


@Task(year=2022, day=18, task=2)
def task02(data: List["Cube"], log: Callable[[AnyStr], None]):
    outside_faces: Set[int] = set()
    visited_droplets: Set[int] = set()
    all_faces: Set[int] = set()
    all_cubes: Set[int] = set()
    for cube in data:
        all_faces.update([hash(face) for face in cube.get_faces()])
        all_cubes.add(hash(cube))
    if len(all_cubes) != len(data):
        raise Exception()
    log(f"Lava-thing consists of {len(all_cubes)} cubes and has {len(all_faces)} faces overall")

    min_x, min_y, min_z = min(c.x for c in data) - 1, min(c.y for c in data) - 1, min(c.z for c in data) - 1
    max_x, max_y, max_z = max(c.x for c in data) + 1, max(c.y for c in data) + 1, max(c.z for c in data) + 1

    droplet_propagation: List[Cube] = [Cube(x=min_x, y=min_y, z=min_z)]
    while len(droplet_propagation) > 0:
        droplet = droplet_propagation.pop(0)
        droplet_hash = hash(droplet)
        if droplet_hash in visited_droplets or droplet_hash in all_cubes:
            continue
        if not (min_x <= droplet.x <= max_x and min_y <= droplet.y <= max_y and min_z <= droplet.z <= max_z):
            continue
        visited_droplets.add(droplet_hash)
        for face in droplet.get_faces():
            face_hash = hash(face)
            if face_hash in all_faces:
                outside_faces.add(face_hash)
        droplet_propagation.extend(droplet.get_neighbors())

    ret = len(outside_faces)
    log(f"In the end there were {len(visited_droplets)} droplets of water and steam outside")
    log(f"Lava-thing has {ret} outside facing faces that get affected by water and steam")
    return len(outside_faces)


@total_ordering
@dataclass(frozen=True)
class Line:
    pt1: Tuple[int, int, int]
    pt2: Tuple[int, int, int]

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)
        return None

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return tuple(sorted((self.pt1, self.pt2))) < tuple(sorted((other.pt1, other.pt2)))
        return None

    def __hash__(self):
        return hash(tuple(sorted((self.pt1, self.pt2))))


@dataclass(frozen=True)
class Face:
    l1: Line
    l2: Line
    l3: Line
    l4: Line

    def __hash__(self):
        ret = hash(tuple(sorted((self.l1, self.l2, self.l3, self.l4))))
        return ret


@dataclass(frozen=True)
class Cube:
    x: int
    y: int
    z: int

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def get_lines(self) -> List[Line]:
        sl = 1
        ret = [
            # Bottom
            Line(pt1=(self.x, self.y, self.z), pt2=(self.x + sl, self.y, self.z)),
            Line(pt1=(self.x + sl, self.y, self.z), pt2=(self.x + sl, self.y + sl, self.z)),
            Line(pt1=(self.x + sl, self.y + sl, self.z), pt2=(self.x, self.y + sl, self.z)),
            Line(pt1=(self.x, self.y + sl, self.z), pt2=(self.x, self.y, self.z)),

            # Top
            Line(pt1=(self.x, self.y, self.z + sl), pt2=(self.x + sl, self.y, self.z + sl)),
            Line(pt1=(self.x + sl, self.y, self.z + sl), pt2=(self.x + sl, self.y + sl, self.z + sl)),
            Line(pt1=(self.x + sl, self.y + sl, self.z + sl), pt2=(self.x, self.y + sl, self.z + sl)),
            Line(pt1=(self.x, self.y + sl, self.z + sl), pt2=(self.x, self.y, self.z + sl)),

            # Bottom to Top
            Line(pt1=(self.x, self.y, self.z), pt2=(self.x, self.y, self.z + sl)),
            Line(pt1=(self.x + sl, self.y, self.z), pt2=(self.x + sl, self.y, self.z + sl)),
            Line(pt1=(self.x + sl, self.y + sl, self.z), pt2=(self.x + sl, self.y + sl, self.z + sl)),
            Line(pt1=(self.x, self.y + sl, self.z), pt2=(self.x, self.y + sl, self.z + sl)),
        ]
        return ret

    def get_faces(self) -> List[Face]:
        lines = self.get_lines()
        ret = [
            # Bottom
            Face(l1=lines[0], l2=lines[1], l3=lines[2], l4=lines[3]),
            # Top
            Face(l1=lines[4], l2=lines[5], l3=lines[6], l4=lines[7]),
            # Sides
            Face(l1=lines[0], l2=lines[4], l3=lines[8], l4=lines[9]),
            Face(l1=lines[1], l2=lines[5], l3=lines[9], l4=lines[10]),
            Face(l1=lines[2], l2=lines[6], l3=lines[10], l4=lines[11]),
            Face(l1=lines[3], l2=lines[7], l3=lines[11], l4=lines[8]),
        ]
        return ret

    def get_neighbors(self) -> List["Cube"]:
        ret = [
            Cube(x=self.x + 1, y=self.y, z=self.z),
            Cube(x=self.x - 1, y=self.y, z=self.z),
            Cube(x=self.x, y=self.y + 1, z=self.z),
            Cube(x=self.x, y=self.y - 1, z=self.z),
            Cube(x=self.x, y=self.y, z=self.z + 1),
            Cube(x=self.x, y=self.y, z=self.z - 1),
        ]
        return ret
