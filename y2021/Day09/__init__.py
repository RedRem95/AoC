import os.path
import time
from typing import Any, Optional, List, Tuple, Dict

import matplotlib.pyplot as plt
import numpy as np
from AoC_Companion.Day import Day, TaskResult


class Day09(Day):

    def __init__(self, year: int, create_img: bool = True):
        super().__init__(year)
        self._create_img = create_img

    def pre_process_input(self, data: Any) -> Any:
        data: List[str] = super().pre_process_input(data=data)
        data = [x for x in data if len(x) > 0]
        ret = np.array([[int(y) for y in x] for x in data], dtype=int)
        return ret

    def run_t1(self, data: np.ndarray) -> Optional[TaskResult]:
        lows = self._find_lows(data=data)
        count_lows = np.sum(lows)
        ret = np.sum(data[lows]) + count_lows
        log = [
            f"The smoke field has a size of {'x'.join(str(x) for x in data.shape)}",
            f"There are {count_lows} low points smoke will flow to and potentially create a basin",
            f"The severity of these low points is {ret}"
        ]
        return TaskResult(ret, log=log)

    def run_t2(self, data: np.ndarray) -> Optional[TaskResult]:
        t1 = time.time()
        lows = self._find_lows(data=data)
        log = [
            f"The smoke field has a size of {'x'.join(str(x) for x in data.shape)}",
            f"There are {np.sum(lows)} low points smoke will flow to and potentially create a basin"
        ]
        pos = list(zip(*np.where(lows)))
        basins: Dict[Tuple[Tuple[int, int], ...], np.ndarray] = {}
        for i, j in pos:
            basin = self._flow(data=data, seed=(i, j), wall_height=9, flown=np.zeros(shape=data.shape, dtype=bool))
            identity = tuple(zip(*np.where(basin)))
            if identity not in basins:
                basins[identity] = basin
        log.append(f"{len(basins)} potential basins found")
        basin_sizes = sorted([np.sum(x) for x in basins.values()], reverse=True)
        n = 3
        ret = np.prod(basin_sizes[:n])
        log.append(f"The {n} largest basins have a size of {' * '.join(str(x) for x in basin_sizes[:n])} = {ret}")
        t2 = time.time()

        if self._create_img:
            fig, axs = plt.subplots(nrows=1, ncols=2)
            try:
                axs = axs.ravel()
            except AttributeError:
                axs = np.array([axs])
            fig: plt.Figure
            fig.set_size_inches(w=25, h=10)
            fig.suptitle(self.get_name())

            ax: plt.Axes = axs[0]
            img = np.zeros(shape=data.shape, dtype=int)
            img[lows] = data[lows]
            im_pos = ax.imshow(img, cmap="binary")
            ax.set_title("The low points smoke will flow to")
            ax.set_xticks([])
            ax.set_yticks([])
            c_bar = fig.colorbar(im_pos, ax=ax)
            c_bar.set_label("Height of the low points")

            ax: plt.Axes = axs[1]
            img = self.create_img(data=data, wall_height=9, lows=lows)
            im_pos = ax.imshow(img, cmap="inferno")
            img = np.ma.masked_where(lows == False, np.ones_like(lows))
            ax.imshow(img, cmap="winter")
            ax.set_title("The smoke field when filled :)")
            ax.axis("off")
            c_bar = fig.colorbar(im_pos, ax=ax)
            c_bar.set_label("Density of smoke field")

            for ax in axs:
                ax.set_xticks([])
                ax.set_yticks([])

            fig.savefig(os.path.join(os.path.dirname(__file__), "visualization.png"))

            self.create_gif(data=data, target=os.path.join(os.path.dirname(__file__), "visualization.gif"))

        return TaskResult(ret, log=log, duration=t2 - t1)

    @staticmethod
    def create_img(data: np.ndarray, wall_height: int = 9, lows: np.ndarray = None) -> np.ndarray:
        if lows is None:
            lows = Day09._find_lows(data=data)
        pos = list(zip(*np.where(lows)))
        basins = [
            Day09._flow(data=data, seed=pt, wall_height=wall_height, flown=np.zeros(shape=data.shape, dtype=bool))
            for pt in pos
        ]
        img = np.zeros(shape=data.shape, dtype=int)
        for basin in basins:
            img[basin] = np.sum(basin)
        return img

    @staticmethod
    def create_gif(data: np.ndarray, target: str, max_wall_height: int = 9):
        import imageio
        from PIL import Image
        from PIL import ImageFont
        from PIL import ImageDraw
        if not target.endswith(".gif"):
            target = f"{target}.gif"

        lows = Day09._find_lows(data=data)

        images = np.array([Day09.create_img(data=data, lows=lows, wall_height=x) for x in range(max_wall_height + 1)])
        min_basin_size, max_basin_size = np.min(images), np.max(images)
        c_map = plt.get_cmap("inferno")(np.arange(min_basin_size, max_basin_size + 1, 1))
        images_colored = (c_map[images] * np.iinfo(np.uint8).max).astype(np.uint8)

        with imageio.get_writer(target, mode='I', format='GIF', duration=1) as writer:
            for i in range(images_colored.shape[0]):
                frame = Image.fromarray(images_colored[i])
                factor = frame.height / frame.width
                frame_width = 500
                frame_height = int(np.ceil(frame_width * factor))
                background = Image.new("RGBA", (frame_width, frame_height + 100), (255, 255, 255, 255))
                frame = Image.fromarray(images_colored[i])
                frame = frame.resize((frame_width, frame_height), resample=Image.NEAREST)
                background.paste(frame, (0, 100))

                box_width = background.width
                box_height = background.height - frame.height
                target_width = box_width / 3
                target_height = box_height / 3
                font = ImageFont.load_default()
                text = f"Iteration {i + 1}/{images_colored.shape[0]}"
                w, h = font.getsize(text=text)
                text_img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
                draw = ImageDraw.Draw(text_img)
                # draw.text((x, y),"Sample Text",(r,g,b))
                draw.text((0, 0), text, (0, 0, 0), font=font)
                factor = target_width / w
                if factor * h > target_height:
                    factor = target_height / h
                text_img = text_img.resize((int(w * factor), int(h * factor)), resample=Image.ANTIALIAS)
                background.paste(
                    text_img,
                    (int((box_width - text_img.width) / 2),
                     int((box_height - text_img.height) / 2))
                )
                writer.append_data(np.asarray(background))
                if i >= images_colored.shape[0] - 1:
                    for _ in range(4):
                        writer.append_data(np.asarray(background))

    @staticmethod
    def _find_lows(data: np.ndarray) -> np.ndarray:
        height_map = np.zeros(shape=np.array(data.shape, dtype=int) + 2, dtype=data.dtype) + np.max(data) + 1
        height_map[1:-1, 1:-1] = data
        lows: np.ndarray = np.ones(shape=data.shape, dtype=bool)

        def moved_height_map(_i: int, _j: int) -> np.ndarray:
            _top, _bottom = 1 + _i, -1 + _i
            _left, _right = 1 + _j, -1 + _j
            _ret = height_map
            if _top >= 0:
                _ret = _ret[_top:, :]
            if _bottom < 0:
                _ret = _ret[:_bottom, :]
            if _left >= 0:
                _ret = _ret[:, _left:]
            if _right < 0:
                _ret = _ret[:, :_right]
            return _ret

        for i, j in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            lows = lows & (moved_height_map(0, 0) < moved_height_map(_i=i, _j=j))
        return lows

    @staticmethod
    def pt_in_data(data: np.ndarray, point: Tuple[int, int]):
        return all(0 <= pt < sh for pt, sh in zip(point, data.shape))

    @staticmethod
    def _flow(data: np.ndarray, seed: Tuple[int, int], wall_height: int = 9, flown: np.ndarray = None) -> np.ndarray:
        i, j = seed
        if not Day09.pt_in_data(data=data, point=seed):
            return flown

        if data[i, j] < wall_height and not flown[i, j]:
            if not flown[i, j]:
                flown[i, j] = True
                for i_n, j_n in [(i + _i, j + _j) for _i, _j in ((1, 0), (-1, 0), (0, 1), (0, -1))]:
                    if Day09.pt_in_data(data=data, point=(i_n, j_n)) and data[i, j] < data[i_n, j_n]:
                        flown = Day09._flow(data=data, seed=(i_n, j_n), wall_height=wall_height, flown=flown)

        return flown
