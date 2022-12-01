from typing import Callable, AnyStr, List, Any, Optional, Dict, Tuple, Iterable, Set, Union, Iterator
import os
import json
import enum
import queue
import itertools
from queue import LifoQueue
from itertools import permutations
from functools import lru_cache

import numpy as np
from scipy.spatial import distance
from scipy.signal import convolve2d
import matplotlib
import matplotlib.pyplot as plt

from AoC_Companion.Day import Task
from AoC_Companion.test import TestData
from AoC_Companion.Preprocess import Preprocessor

_pt_type = np.ndarray

with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f_config:
    _config = json.load(f_config)


@Preprocessor(year=2021, day=20)
def pre_process_input(data: Any) -> Tuple[np.ndarray, np.ndarray]:
    data = [x for x in data if len(x) > 0]
    algorithm = np.array([1 if x == "#" else 0 for x in data[0]], dtype=np.uint16)

    image = np.array([[1 if x == "#" else 0 for x in line] for line in data[1:]], dtype=np.uint16)

    return algorithm, image


@Task(year=2021, day=20, task=1, extra_config=_config)
def run_t1(
        data: Tuple[np.ndarray, np.ndarray], log: Callable[[str], None], steps: Dict[str, int], create_visual: bool
) -> Any:
    return run(data=data, log=log, steps=steps["1"], create_visual=create_visual)


@Task(year=2021, day=20, task=2, extra_config=_config)
def run_t2(
        data: Tuple[np.ndarray, np.ndarray], log: Callable[[str], None], steps: Dict[str, int], create_visual: bool
) -> Any:
    return run(data=data, log=log, steps=steps["2"], create_visual=create_visual)


def run(data: Any, log: Callable[[str], None], steps: int, create_visual: bool) -> Any:
    algorithm, image = data
    images = [image]
    for i in range(steps):
        image = step(image=image, algorithm=algorithm, i=i)
        images.append(image)
    ret = np.sum(image)
    log(f"Initial image had a size of {images[0].shape[1]}x{images[0].shape[0]}")
    log(f"Running enhancement for {steps} steps")
    log(f"Final image has a size of {images[-1].shape[1]}x{images[-1].shape[0]}")
    log(f"  In the final image {ret} pixels where lit")
    if create_visual:
        target = os.path.join(os.path.dirname(__file__), f"Day20-{steps}.gif")
        log(f"Saving gif to {target}")
        create_gif(*images, target=target, algorithm=algorithm)
    return ret


def step(image: np.ndarray, algorithm: np.ndarray, size: int = 3, i: int = 0) -> np.ndarray:
    kernel = (2 ** np.arange(size * size)).reshape((size, size))
    void_val = get_void(algorithm=algorithm, i=i)
    # image = np.pad(image, 2, mode="constant", constant_values=void_val)
    image_conv2d = convolve2d(image, kernel, mode="full", fillvalue=void_val)
    image = algorithm[image_conv2d].astype(image.dtype)
    return image


def get_void(algorithm: np.ndarray, i: int):
    if algorithm[0] == algorithm[-1]:
        return algorithm[0]
    if algorithm[0] == 0:
        return 0
    return i % 2


def create_gif(*images: np.ndarray, target: str, algorithm: np.ndarray):
    import imageio

    max_size = np.array(tuple(max(img.shape[i] for img in images) for i in range(len(images[0].shape))))

    def scale_img(_img: np.ndarray, _void_val: Union[int, float]) -> np.ndarray:
        try:
            from skimage.transform import resize
            return resize(_img, output_shape=max_size, mode="constant", cval=_void_val)
        except ImportError:
            _img = _img.astype(float)
            pad_size = []
            for _i in range(len(_img.shape)):
                diff = max_size[_i] - _img.shape[_i]
                d2 = diff // 2
                d1 = diff - d2
                pad_size.append((d1, d2))
            return np.pad(_img, pad_size, mode="constant", constant_values=_void_val)

    with imageio.get_writer(target, mode='I', format='GIF', duration=1 / 4) as writer:
        for i, image_arr in enumerate(images):
            void_val = get_void(algorithm=algorithm, i=i)
            image_arr = (np.clip(image_arr, 0, 1) * np.iinfo(np.uint8).max).astype(np.uint8)
            image_arr = scale_img(_img=image_arr, _void_val=void_val)
            image_arr = (np.clip(image_arr, 0, 1) * np.iinfo(np.uint8).max).astype(np.uint8)

            writer.append_data(image_arr)
            if i == len(images) - 1:
                for _ in range(9):
                    writer.append_data(image_arr)
