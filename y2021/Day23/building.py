import copy
import math
import queue
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Iterable, Tuple, Any, Union, Callable, Dict


class AmphipodTypes(Enum):
    Amber = "A"
    Bronze = "B"
    Copper = "C"
    Desert = "D"

    def get_cost(self) -> int:
        return {
            AmphipodTypes.Amber: 1,
            AmphipodTypes.Bronze: 10,
            AmphipodTypes.Copper: 100,
            AmphipodTypes.Desert: 1000
        }[self]

    def get_room_idx(self) -> int:
        return sorted([x for x in self.__class__], key=lambda x: x.value).index(self)

    @classmethod
    def get_by_value(cls, v: str) -> Optional["AmphipodTypes"]:
        for typ in cls:
            if typ.value == v:
                return typ
        return None

    @classmethod
    def get_by_idx(cls, idx) -> Optional["AmphipodTypes"]:
        for typ in cls:
            if typ.get_room_idx() == idx:
                return typ
        return None


class Amphipod:
    def __init__(self, typ: AmphipodTypes):
        self.typ = typ

    def __str__(self):
        return self.typ.value

    def __repr__(self):
        return f"<{self.typ.name}-{self.__class__.__name__}>"

    def __copy__(self) -> "Amphipod":
        return self.__class__(typ=self.typ)


class RoomFullException(Exception):
    pass


class OccupiedException(Exception):
    pass


class Room:
    def __init__(self, occupant: AmphipodTypes, initial: List[Amphipod], spaces: Optional[int] = None):
        if spaces is None:
            spaces = len(initial)
        if occupant is None:
            raise ValueError()
        self.occupant = occupant
        self.spaces: List[Optional[Amphipod]] = [None for _ in range(spaces)]
        for amp in initial:
            self._add(member=amp)

    def __copy__(self) -> "Room":
        copy_spaces = [copy.copy(x) for x in self.spaces]
        return self.__class__(occupant=self.occupant, initial=list(reversed(copy_spaces)), spaces=len(self))

    def _add(self, member: Amphipod) -> int:
        for i in range(1, len(self) + 1):
            if self.spaces[-i] is None:
                self.spaces[-i] = member
                return len(self) - i + 1
        raise RoomFullException("Room is full")

    def room_happy(self) -> bool:
        for space in self.spaces:
            if space is not None and space.typ != self.occupant:
                return False
        return True

    def has_space(self) -> bool:
        return self.spaces[0] is None

    def accept(self, new_member: Amphipod) -> bool:
        return new_member.typ == self.occupant and self.has_space() and self.room_happy()

    def place(self, new_member: Amphipod) -> Union["Amphipod", int]:
        if not self.accept(new_member=new_member):
            return new_member
        return self._add(member=new_member)

    def place_cost(self) -> int:
        for i in range(1, len(self) + 1):
            if self.spaces[-i] is None:
                return len(self) - i + 1

    def get(self, remove: bool = False) -> Optional[Tuple[int, "Amphipod"]]:
        if not self.has_space() and self.room_happy():
            return None
        for i in range(len(self)):
            if self.spaces[i] is not None:
                ret = self.spaces[i]
                if remove:
                    self.spaces[i] = None
                return i + 1, ret

    def __len__(self):
        return len(self.spaces)

    def __str__(self):
        return "".join(" " if x is None else str(x) for x in self.spaces)

    def __repr__(self):
        return f"<{self.occupant.name}-Room: {str(self)}>"


class HallwayTile:
    def __init__(self):
        self.element: Optional[Amphipod] = None
        self.room: Optional[Room] = None

    def get(self, remove: bool = False) -> Optional[Amphipod]:
        ret = self.element
        if remove:
            self.element = None
        return ret

    def is_free(self) -> bool:
        return self.get() is None

    def set(self, new_element: Optional[Amphipod]):
        if new_element is not None and not self.is_free():
            raise OccupiedException("Space not free")
        self.element = new_element

    def set_room(self, room: Room):
        if self.room is not None:
            raise OccupiedException("Room already set")
        self.room = room

    def get_room(self) -> Optional[Room]:
        return self.room

    def can_leave_room(self) -> bool:
        return self.get_room() is not None and self.is_free()

    def __str__(self):
        return "." if self.is_free() else str(self.get())

    def __repr__(self):
        return f"<{self.__class__.__name__}: " \
               f"{'free' if self.is_free() else str(self.element)}, " \
               f"{'no-room' if self.get_room() is None else repr(self.get_room())}>"

    def __copy__(self) -> "HallwayTile":
        ret = HallwayTile()
        ret.set(copy.copy(self.get()))
        ret.set_room(copy.copy(self.get_room()))
        return ret


class Hallway:
    def __init__(self, size: int):
        self.hallway: List[HallwayTile] = [HallwayTile() for _ in range(size)]

    def __len__(self):
        return len(self.hallway)

    def _set_tile(self, idx: int, hallway_tile: HallwayTile):
        self.hallway[idx] = hallway_tile

    def set_room(self, idx: int, room: Room):
        self.hallway[idx].set_room(room=room)

    def get_rooms(self) -> List[Tuple[HallwayTile, Room]]:
        ret = []
        for tile in self:
            if tile.get_room() is not None:
                ret.append((tile, tile.get_room()))
        return ret

    def can_reach(self, origin: HallwayTile, target: HallwayTile) -> bool:
        id_origin = self.get_tile_idx(origin)
        id_target = self.get_tile_idx(target)
        if id_origin == id_target:
            return True
        sgn = int(math.copysign(1, id_target - id_origin))
        for i in range(id_origin, id_target, sgn):
            if i == id_origin:
                continue
            if not self[i].is_free():
                return False
        return True

    def cost(self, origin: HallwayTile, target: HallwayTile) -> int:
        id_origin = self.get_tile_idx(origin)
        id_target = self.get_tile_idx(target)
        return abs(id_target - id_origin)

    def get_tile_idx(self, tile: HallwayTile):
        return self.hallway.index(tile)

    def set_amphipod(self, idx: int, amphipod: Amphipod):
        self.hallway[idx].set(new_element=amphipod)

    def hallway_empty(self) -> bool:
        return all(x.is_free() for x in self)

    def rooms_happy(self) -> bool:
        for tile, room in self.get_rooms():
            if not room.room_happy():
                return False
        return True

    def hallway_score(self) -> int:
        half_way = len(self) // 2
        lst = [((i - half_way) ** 2) * (0 if self[i].is_free() else 1) for i in range(len(self))]
        return sum(lst)

    def done(self):
        return self.hallway_empty() and self.rooms_happy()

    def __getitem__(self, item: int) -> HallwayTile:
        return self.hallway[item]

    def __iter__(self) -> Iterable[HallwayTile]:
        for tile in self.hallway:
            yield tile

    def __str__(self):
        max_room_depth = max([len(room) for tile, room in self.get_rooms()] + [0])
        lines = [[] for _ in range(max_room_depth + 3)]

        def insert_col(col: str):
            lines[0].append("#")
            i = -1
            for i, c in enumerate(col):
                lines[i + 1].append(c)
            for j in range(i + 2, len(lines)):
                lines[j].append("#")

        insert_col("")
        for tile in self:
            insert_col(f"{tile}{'' if tile.get_room() is None else str(tile.get_room())}")
        insert_col("")
        return "\n".join("".join(line) for line in lines)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {', '.join(repr(x) for x in self.hallway)}>"

    def __copy__(self) -> "Hallway":
        ret = Hallway(size=len(self))
        for i, tile in enumerate(self):
            ret._set_tile(idx=i, hallway_tile=copy.copy(tile))
        return ret


class State:
    _COUNTER = 0

    @classmethod
    def solve(cls, init_state: "State") -> Optional["State"]:

        import tqdm

        current_states: queue.Queue[StateCreationPackage] = queue.PriorityQueue()
        current_states.put(StateCreationPackage(init_state.energy, lambda **x: init_state, {}))

        with tqdm.tqdm(desc="Running") as pb:
            while not current_states.empty():
                pb.update()
                creation_package = current_states.get()
                state_creator, data = creation_package.creation_function, creation_package.data
                state = state_creator(**data)
                if state.done():
                    return state
                pb.set_description(desc=f"Running on energy {state.energy}")
                new_states = state.new_states()
                # print("-" * 10, "FROM-STATE", "-" * 10)
                # print(states[-1])
                # print("-" * 10, " NEW-STATE", "-" * 10)
                # print(f"\n{'-'*10}\n".join(str(x) for x in new_states))
                for new_state in new_states:
                    current_states.put(new_state)

        return None

    def __init__(self, hallway: Hallway, energy: int = 0):
        self.hallway = hallway
        self.id = self.__class__._COUNTER
        self.__class__._COUNTER += 1
        self.energy = energy

    def new_states(self) -> List["StateCreationPackage"]:
        ret: List[StateCreationPackage] = []

        hallway_candidates: List[Tuple[int, HallwayTile]] = [(i, x) for i, x in enumerate(self.hallway) if
                                                             not x.is_free()]
        for idx, candidate in hallway_candidates:
            potential_targets = self.hallway.get_rooms()
            element = candidate.get(remove=False)
            potential_targets = [(tile, room) for tile, room in potential_targets if tile.is_free()]
            potential_targets = [(tile, room) for tile, room in potential_targets if
                                 self.hallway.can_reach(candidate, tile)]
            potential_targets = [(tile, room) for tile, room in potential_targets if room.accept(new_member=element)]
            for target_tile, target_room in potential_targets:
                new_energy = (self.hallway.cost(candidate, target_tile) + target_room.place_cost())
                new_energy *= element.typ.get_cost()
                new_energy += self.energy
                data = {"origin_idx": idx,
                        "target_idx": self.hallway.get_tile_idx(target_tile),
                        "hallway": self.hallway,
                        "energy": new_energy}
                ret.append(StateCreationPackage(new_energy, self.create_state_hallway, data))
            # return ret

        room_candidates = [(tile, room) for tile, room in self.hallway.get_rooms() if tile.is_free()]
        room_candidates = [(tile, room) for tile, room in room_candidates if room.get(remove=False) is not None]
        for tile, room in room_candidates:
            potential_targets = [(i, t) for i, t in enumerate(self.hallway) if t.is_free()]
            potential_targets = [(i, t) for i, t in potential_targets if self.hallway.can_reach(tile, t)]
            potential_targets = [(i, t) for i, t in potential_targets if t.get_room() is None]
            tile_idx = self.hallway.get_tile_idx(tile)
            el_cost, el = room.get(remove=False)
            for target_idx, target_tile in potential_targets:
                new_energy = (self.hallway.cost(tile, target_tile) + el_cost) * el.typ.get_cost() + self.energy
                data = {"origin_idx": tile_idx,
                        "target_idx": target_idx,
                        "hallway": self.hallway,
                        "energy": new_energy}
                ret.append(StateCreationPackage(new_energy, self.create_state_room, data))
            # return [ret[0]]

        return ret

    @staticmethod
    def create_state_hallway(origin_idx: int, target_idx: int, hallway: Hallway, energy: int) -> "State":
        new_hallway = copy.copy(hallway)
        move_element = new_hallway[origin_idx].get(remove=True)
        new_room = new_hallway[target_idx].get_room()
        new_room.place(move_element)
        return State(hallway=hallway, energy=energy)

    @staticmethod
    def create_state_room(origin_idx: int, target_idx: int, hallway: Hallway, energy: int) -> "State":
        new_hallway = copy.copy(hallway)
        _, move_element = new_hallway[origin_idx].get_room().get(remove=True)
        new_tile = new_hallway[target_idx]
        new_tile.set(new_element=move_element)
        return State(hallway=new_hallway, energy=energy)

    def done(self) -> bool:
        return self.hallway.done()

    def __str__(self):
        return f"State:  {self.id:6d}\nEnergy: {self.energy:6d}\n{self.hallway}"

    def __lt__(self, other):
        if not isinstance(other, State):
            return True
        return self.energy < other.energy

    def __le__(self, other):
        if not isinstance(other, State):
            return True
        return self.energy <= other.energy

    def __gt__(self, other):
        if not isinstance(other, State):
            return True
        return self.energy > other.energy

    def __ge__(self, other):
        if not isinstance(other, State):
            return True
        return self.energy >= other.energy

    def __eq__(self, other):
        if not isinstance(other, State):
            return True
        return self.id == other.id and self.energy == other.energy

    def __ne__(self, other):
        if not isinstance(other, State):
            return True
        return not self == other


@dataclass(order=True)
class StateCreationPackage:
    energy: int
    creation_function: Callable[[int, int, Hallway, int], "State"] = field(compare=False)
    data: Dict[str, Any] = field(compare=False)
