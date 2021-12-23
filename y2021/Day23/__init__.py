from typing import Any, Optional, List, Dict

from AoC_Companion.Day import Day, TaskResult

from y2021.Day23.building import Hallway, Amphipod, AmphipodTypes, Room, State


class Day23(Day):

    def __init__(self, year: int):
        super().__init__(year)

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
        hallway = Hallway(size=hallway_len)
        for j, (idx, room) in enumerate(sorted(room_stuff.items(), key=lambda x: x[0])):
            room = Room(occupant=AmphipodTypes.get_by_idx(j), initial=list(reversed(room)))
            hallway.set_room(room=room, idx=idx)
        return hallway

    def run_t1(self, data: Hallway) -> Optional[TaskResult]:
        state = State(hallway=data)
        solved_state = State.solve(init_state=state)
        log = []
        log.append("From:")
        log.extend(str(data).split("\n"))
        log.append("")
        log.append("To:")
        log.extend(str(solved_state).split("\n"))
        return TaskResult(solved_state.energy, log=log)

    def run_t2(self, data: Any) -> Optional[TaskResult]:
        return TaskResult(None)
