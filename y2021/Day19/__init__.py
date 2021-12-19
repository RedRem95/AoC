import itertools
import os.path
import queue
from typing import Any, Optional, List, Tuple, Iterator, Dict, Set

import matplotlib.lines
import matplotlib.pyplot as plt
import numpy as np
from AoC_Companion.Day import Day, TaskResult
from scipy.spatial import distance


class Day19(Day):
    pt_type = np.ndarray
    scan_type = np.ndarray
    _OFFSET_CACHE: Dict[Tuple[Tuple[int, ...]], List[Tuple[pt_type, Set[Tuple[int, ...]]]]] = {}

    def __init__(self, year: int, visualization: bool = True, force_reset: bool = False):
        super().__init__(year)
        self._visualization = visualization
        self._data: Optional[Tuple[Dict[Tuple[int, int, int], Day19.scan_type], Day19.scan_type]] = None
        self._force_reset = force_reset

    def pre_process_input(self, data: Any) -> List[scan_type]:
        data: List[str] = super().pre_process_input(data=data)
        scanners: List[Day19.scan_type] = []
        current_scanner: List[Tuple[int, ...]] = []
        for line in data:
            line = line.strip()
            if len(line) <= 0:
                continue
            elif line.startswith("---"):
                if len(current_scanner) > 0:
                    scanners.append(np.array(current_scanner))
                current_scanner = []
            else:
                current_scanner.append(tuple(int(x) for x in line.split(",")))
                if len(current_scanner[-1]) != 3 and False:
                    raise Exception()
        if len(current_scanner) > 0:
            scanners.append(np.array(current_scanner))
        return scanners

    def run_t1(self, data: List[scan_type]) -> Optional[TaskResult]:
        if self._force_reset:
            self.reset()
        if self._data is None:
            self._data = self.find_scanners_and_probes(data=data)
        scanners, probes = self._data
        return TaskResult(probes.shape[0])

    def run_t2(self, data: Any) -> Optional[TaskResult]:
        if self._force_reset:
            self.reset()
        if self._data is None:
            self._data = self.find_scanners_and_probes(data=data)
        scanners, probes = self._data
        scanner_positions = np.array([x for x in scanners.keys()])
        combinations = itertools.combinations(range(scanner_positions.shape[0]), 2)
        distances = [(i, j, distance.cityblock(scanner_positions[i], scanner_positions[j])) for i, j in combinations]
        if self._visualization:
            f_name = os.path.join(os.path.dirname(__file__), "map.png")
            fig = self.plot(scanners=scanners, probes=probes)
            fig.set_size_inches(15, 15)
            fig.set_dpi(300)
            fig.savefig(f_name)
        return TaskResult(int(max(x[-1] for x in distances)))

    def reset(self):
        self._data = None
        self.__class__._OFFSET_CACHE.clear()

    @staticmethod
    def find_scanners_and_probes(data: List[scan_type]) -> Tuple[Dict[Tuple[int, int, int], scan_type], scan_type]:
        probes: Day19.scan_type = data[0].copy()
        scanner_positions: Dict[Tuple[int, int, int], Day19.scan_type] = {(0, 0, 0): data[0]}
        unsafe: queue.Queue[Tuple[int, Day19.scan_type]] = queue.Queue(len(data) - 1)
        for i, d in enumerate(data[1:]):
            unsafe.put((i + 1, d))

        while not unsafe.empty():
            i, candidate = unsafe.get()
            found = False
            for moved_scanner in Day19.permute_scanner(base=candidate):
                common = Day19.find_common_beacons(scanner1=probes, scanner2=moved_scanner)
                if common is not None:
                    common1, common2, confidence = common
                    scanner_pos = common1 - common2
                    probe_pos = moved_scanner + scanner_pos
                    scanner_positions[tuple(scanner_pos)] = probe_pos
                    probes = np.unique(np.concatenate((probes, probe_pos), axis=0), axis=0)
                    found = True
                    break
            if not found:
                if unsafe.empty():
                    raise Exception(f"There was no way to determine scanner {i}")
                unsafe.put((i, candidate))

        return scanner_positions, probes

    @staticmethod
    def permute_scanner(base) -> Iterator[scan_type]:
        for dir_x, dir_y in itertools.permutations(range(3), 2):
            for sign_x, sign_y in itertools.product((-1, 1), (-1, 1)):
                x_vec = np.zeros((3,))
                y_vec = np.zeros((3,))
                x_vec[dir_x] = sign_x
                y_vec[dir_y] = sign_y
                z_vec = np.cross(x_vec, y_vec)

                ret = np.stack((np.dot(base, x_vec), np.dot(base, y_vec), np.dot(base, z_vec)), axis=1)

                yield ret

    @classmethod
    def get_offset_dict(cls, scanner: scan_type) -> List[Tuple[pt_type, Set[Tuple[int, ...]]]]:
        unique_identifier: Tuple[Tuple[int, ...]] = tuple({tuple(x) for x in scanner})
        if unique_identifier not in cls._OFFSET_CACHE:
            tmp_identifier = np.array(unique_identifier)
            offset_dict: List[Tuple[Day19.pt_type, Set[Tuple[int, ...]]]] = []
            for x in tmp_identifier:
                tmp = x - tmp_identifier
                offset_dict.append((x, set(tuple(y) for y in tmp)))
            offset_dict: List[Tuple[Day19.pt_type, Set[Tuple[int, ...]]]] = [
                (x, set(tuple(x - y) for y in tmp_identifier)) for x in tmp_identifier
            ]
            cls._OFFSET_CACHE[unique_identifier] = offset_dict
        return cls._OFFSET_CACHE[unique_identifier]

    @staticmethod
    def find_common_beacons(scanner1: scan_type, scanner2: scan_type) -> Optional[Tuple[pt_type, pt_type, int]]:

        offsets1 = Day19.get_offset_dict(scanner=scanner1)
        offsets2 = Day19.get_offset_dict(scanner=scanner2)

        if len(offsets1) != scanner1.shape[0] or len(offsets2) != scanner2.shape[0]:
            raise Exception()

        for s1, s1o in offsets1:
            for s2, s2o in offsets2:
                intersecting_points = len(set.intersection(s1o, s2o))
                if intersecting_points >= 12:
                    return np.array(s1), np.array(s2), intersecting_points

        return None

    @staticmethod
    def plot(scanners: Dict[Tuple[int, int, int], scan_type], probes: scan_type) -> plt.Figure:
        fig: plt.Figure = plt.figure()
        ax: plt.Axes = fig.add_subplot(projection='3d')
        c_map = plt.get_cmap("autumn")
        legend_elements = [
            matplotlib.lines.Line2D([0], [0], marker='x', label='Scanners', markerfacecolor='black'),
            matplotlib.lines.Line2D([0], [0], marker='o', label='Probes', markerfacecolor='black')
        ]
        for i, (scanner_pos, scanner_probes) in enumerate(scanners.items()):
            ax.scatter(scanner_pos[0], scanner_pos[1], scanner_pos[2],
                       marker="x", label=f"Scanner {scanner_pos}", color=c_map(i / len(scanners)))
            ax.scatter(scanner_probes[:, 0], scanner_probes[:, 1], scanner_probes[:, 2],
                       marker="o", label=f"Probes {scanner_pos}", color=c_map(i / len(scanners)))
            # legend_elements.append(
            #     matplotlib.lines.Line2D([0], [0], color=c_map(i/len(scanners)), label=f"{scanner_pos}", lw=2)
            # )

        # ax.axis("off")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.legend(handles=legend_elements, loc="best")

        return fig
