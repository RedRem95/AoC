import os.path
import time
from typing import Any, Optional, List, Tuple, Dict, Union

import numpy as np
from AoC_Companion.Day import Day, TaskResult, StarTask
from scipy.signal import convolve2d
from skimage.transform import resize


class Day20(Day):
    _pt_type = np.ndarray

    def __init__(self, year: int, steps: Optional[Dict[str, int]] = None, create_visual: bool = False):
        super().__init__(year)
        self._steps: Dict[int, int] = {} if steps is None else {int(k): v for k, v in steps.items()}
        self._create_visual = create_visual if isinstance(create_visual, bool) else False

    def pre_process_input(self, data: Any) -> Tuple[np.ndarray, np.ndarray]:
        data: List[str] = super().pre_process_input(data=data)
        data = [x for x in data if len(x) > 0]
        algorithm = np.array([1 if x == "#" else 0 for x in data[0]], dtype=np.uint16)

        image = np.array([[1 if x == "#" else 0 for x in line] for line in data[1:]], dtype=np.uint16)

        return algorithm, image

    def run(self, task: StarTask, data: Any) -> Optional[TaskResult]:
        t1 = time.time()
        algorithm, image = data
        steps = self._steps.get(task.value, 1)
        images = [image]
        for i in range(steps):
            image = self.step(image=image, algorithm=algorithm, i=i)
            images.append(image)
        ret = np.sum(image)
        log = [
            f"Initial image had a size of {images[0].shape[1]}x{images[0].shape[0]}",
            f"Running enhancement for {steps} steps",
            f"Final image has a size of {images[-1].shape[1]}x{images[-1].shape[0]}",
            f"  In the final image {ret} pixels where lit"
        ]
        t2 = time.time()
        if self._create_visual:
            target = os.path.join(os.path.dirname(__file__), f"{task.name}-{steps}.gif")
            log.append(f"Saving gif to {target}")
            self.create_gif(*images, target=target, algorithm=algorithm)
        return TaskResult(ret, day=self, task=task, duration=t2 - t1, log=log)

    def run_t1(self, data: Tuple[np.ndarray, np.ndarray]) -> Optional[TaskResult]:
        pass

    def run_t2(self, data: Tuple[np.ndarray, np.ndarray]) -> Optional[TaskResult]:
        pass

    @staticmethod
    def step(image: np.ndarray, algorithm: np.ndarray, size: int = 3, i: int = 0) -> np.ndarray:
        kernel = (2 ** np.arange(size * size)).reshape((size, size))
        void_val = Day20.get_void(algorithm=algorithm, i=i)
        # image = np.pad(image, 2, mode="constant", constant_values=void_val)
        image_conv2d = convolve2d(image, kernel, mode="full", fillvalue=void_val)
        image = algorithm[image_conv2d].astype(image.dtype)
        return image

    @staticmethod
    def get_void(algorithm: np.ndarray, i: int):
        if algorithm[0] == algorithm[-1]:
            return algorithm[0]
        if algorithm[0] == 0:
            return 0
        return i % 2

    @staticmethod
    def create_gif(*images: np.ndarray, target: str, algorithm: np.ndarray):
        import imageio

        max_size = np.array(tuple(max(img.shape[i] for img in images) for i in range(len(images[0].shape))))

        def scale_img(_img: np.ndarray, _void_val: Union[int, float]) -> np.ndarray:
            return resize(_img, output_shape=max_size, mode="constant", cval=_void_val)
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
                void_val = Day20.get_void(algorithm=algorithm, i=i)
                image_arr = (np.clip(image_arr, 0, 1) * np.iinfo(np.uint8).max).astype(np.uint8)
                image_arr = scale_img(_img=image_arr, _void_val=void_val)
                image_arr = (np.clip(image_arr, 0, 1) * np.iinfo(np.uint8).max).astype(np.uint8)

                writer.append_data(image_arr)
                if i == len(images) - 1:
                    for _ in range(9):
                        writer.append_data(image_arr)
