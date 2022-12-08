from typing import Callable, AnyStr, List, Tuple
import os

import numpy as np

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor


@Preprocessor(year=2022, day=8)
def preproc_1(data):
    ret = []
    for line in data:
        line = line.strip()
        if len(line) <= 0:
            continue
        ret.append([int(x) for x in line])
    return np.array(ret)


@Task(year=2022, day=8, task=1, extra_config={"draw": False})
def task01(data: np.ndarray, log: Callable[[AnyStr], None], draw: bool):
    visible = _calc_visible_map(data=data, log=log)
    if draw:
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            fig, ax = plt.subplots()
            fig.set_size_inches(5, 5)
            fig.suptitle(f"Visibility map ({'x'.join(str(x) for x in data.shape)} trees)")
            im = ax.imshow(visible, interpolation=None)
            v = np.unique(visible.ravel())
            colors = [im.cmap(im.norm(value)) for value in v]
            patch_list = [patches.Patch(color=colors[i], label=f"{'' if i else 'in'}visible") for i in range(len(v))]
            ax.legend(handles=patch_list, bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
            fig.savefig(os.path.join(os.path.dirname(__file__), "visible_map.png"), dpi=600, format="png")
        except ImportError:
            plt, patches = None, None
    return np.sum(visible)


@Task(year=2022, day=8, task=2, extra_config={"draw": False, "use_vis": False})
def task02(data, log: Callable[[AnyStr], None], draw: bool, use_vis: bool):
    vis_map = _calc_visible_map(data=data, log=lambda x: None) if use_vis else None
    scenic_score = _calc_scenic_score(data=data, log=log, vis_map=vis_map)
    if draw:
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            fig, ax = plt.subplots(1, 1 if vis_map is None else 2)
            fig.suptitle(f"Scenic scores ({'x'.join(str(x) for x in data.shape)} trees)")
            ax = np.array([ax]).ravel()
            fig.set_size_inches(5 * len(ax), 5)
            v_min, v_max = np.min(scenic_score), np.max(scenic_score)
            im = ax[0].imshow(scenic_score, vmin=v_min, vmax=v_max, aspect="equal", interpolation=None)
            fig.colorbar(im)
            if vis_map is not None:
                ax[0].set_title("Considering all spots")
                ax[1].set_title("Considering only hidden spots")
                scenic_score_masked = scenic_score.copy()
                scenic_score_masked[vis_map] = 0
                v_min, v_max = np.min(scenic_score), np.max(scenic_score_masked)
                im = ax[1].imshow(scenic_score_masked, vmin=v_min, vmax=v_max, aspect="equal", interpolation=None)
                fig.colorbar(im)
            fig.savefig(os.path.join(os.path.dirname(__file__), "scenic_scores.png"), dpi=600, format="png")
        except ImportError:
            plt, patches = None, None
    return np.max(scenic_score)


def _calc_visible_map(data: np.ndarray, log: Callable[[AnyStr], None]) -> np.ndarray:
    log(f"Calculating visibility map on {'x'.join(str(x) for x in data.shape)} ({np.prod(data.shape)}) trees")
    visible = np.zeros(shape=data.shape, dtype=bool)
    visible[0, :] = True
    visible[-1:, ] = True
    visible[:, 0] = True
    visible[:, -1] = True

    if data.shape[0] != data.shape[1] or len(data.shape) != 2:
        log(f"The map has to be squared and only 2d")
        raise Exception()

    for i in range(1, data.shape[0] - 1):
        for j in range(1, data.shape[1] - 1):
            if any(x[0] for x in _check(i, j, data)):
                visible[i, j] = True

    log(f"{np.sum(visible)} trees are visible. That are {100 * np.sum(visible) / np.prod(data.shape):.2f}%")

    return visible


def _calc_scenic_score(data: np.ndarray, log: Callable[[AnyStr], None], vis_map: np.ndarray = None) -> np.ndarray:
    log(f"Calculating scenic score on {'x'.join(str(x) for x in data.shape)} ({np.prod(data.shape)}) trees")
    scenic_score = np.zeros(shape=data.shape, dtype=int)

    if data.shape[0] != data.shape[1] or len(data.shape) != 2:
        raise Exception()

    for i in range(1, data.shape[0] - 1):
        for j in range(1, data.shape[1] - 1):
            checked = _check(i, j, data)
            scenic_score[i, j] = np.prod([x[1] for x in checked])

    max_loc = list(zip(*np.where(scenic_score == np.max(scenic_score))))
    log(f"The highest scenic score is at {max_loc[0]} with {scenic_score[max_loc[0]]}")
    log(f"The average scenic score is {np.mean(scenic_score):.2f}")

    if vis_map is not None:
        max_loc_masked = list(zip(*np.where(scenic_score == np.max(scenic_score[vis_map == False]))))
        log(f"The highest hidden scenic score is at {max_loc_masked[0]} with {scenic_score[max_loc_masked[0]]}")
        log(f"The average hidden scenic score is {np.mean(scenic_score[vis_map == False]):.2f}")

    return scenic_score


def _check(i, j, data) -> List[Tuple[bool, int]]:
    ret = [(False, -1), (False, -1), (False, -1), (False, -1)]
    block = np.where(data[:i, j] >= data[i, j])[0]
    ret[0] = (len(block) <= 0, i - max([*block, 0]))
    block = np.where(data[i+1:, j] >= data[i, j])[0]
    ret[1] = (len(block) <= 0, min([*block, data.shape[0] - i - 2])+1)
    block = np.where(data[i, :j] >= data[i, j])[0]
    ret[2] = (len(block) <= 0, j - max([*block, 0]))
    block = np.where(data[i, j+1:] >= data[i, j])[0]
    ret[3] = (len(block) <= 0, min([*block, data.shape[0]-j-2])+1)
    return ret
