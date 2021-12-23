from typing import Any, Optional, List, Dict

from AoC_Companion.Day import Day, TaskResult

from y2021.Day23.building import Hallway, Amphipod, AmphipodTypes, Room, State


class Day23(Day):

    def __init__(self, year: int, longer_rooms: Dict[str, str]):
        super().__init__(year)
        if not all(len(x) for x in longer_rooms.values()):
            raise Exception()
        self.longer_rooms = {int(k): list(Amphipod.parse_from_str(data=v)) for k, v in longer_rooms.items()}

    def pre_process_input(self, data: Any) -> Any:
        data: List[str] = super().pre_process_input(data=data)
        data: List[str] = [x for x in data if len(x) > 0]
        hallway_len = 0
        i = data[1].index(".")
        for j in range(i, len(data[1])):
            if data[1][i] == ".":
                hallway_len += 1
                continue
            break
        room_stuff: Dict[int, List[Amphipod]] = {}
        for line in data[2:]:
            for j, c in enumerate(line[1:]):
                typ = AmphipodTypes.get_by_value(v=c)
                if typ is not None:
                    if j not in room_stuff:
                        room_stuff[j] = []
                    room_stuff[j].append(Amphipod(typ=typ))
        hallway = Hallway(size=hallway_len-1)
        for j, (idx, room) in enumerate(sorted(room_stuff.items(), key=lambda x: x[0])):
            room = Room(occupant=AmphipodTypes.get_by_idx(j), initial=list(reversed(room)))
            hallway.set_room(room=room, idx=idx)
        return hallway

    def run_t1(self, data: Hallway) -> Optional[TaskResult]:
        return self._run(data=data)

    def run_t2(self, data: Hallway) -> Optional[TaskResult]:
        for i, (_, room) in enumerate(data.get_rooms()):
            room.insert(1, self.longer_rooms[i])
        return self._run(data=data)

    @staticmethod
    def _run(data: Hallway) -> TaskResult:
        state = State(hallway=data)
        solve_energy, solved_hallway = State.solve(init_state=state)
        log = []
        log.append("From:")
        log.extend(str(data).split("\n"))
        log.append("")
        log.append(f"To (Used Energy: {solve_energy}):")
        log.extend(str(solved_hallway).split("\n"))
        return TaskResult(solve_energy, log=log)