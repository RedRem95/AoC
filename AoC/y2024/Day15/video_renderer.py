import os
from typing import Callable, AnyStr


class VideoRenderer:
    def __init__(self, f_name: str, fps: int, log: Callable[[AnyStr], None] = None, final_as_img: bool = False):
        if log is None:
            def log(*args): return None
        self._log = log
        self._fname = f_name
        self._writer = None
        self._last_img = None
        self._final_as_img = final_as_img
        if f_name is not None and len(f_name) > 0:
            try:
                import imageio as iio
                from PIL import Image
                self._writer = iio.get_writer(
                    f_name, fps=fps, codec="libx264", quality=6, ffmpeg_log_level="quiet", macro_block_size=16
                )
            except ImportError as e:
                self._log(f"Failed to render video cause of missing libraries: {e.name}")
            except Exception as e:
                self._log(f"Failed to create renderer for video: {e}")

    def add_frame(self, frame, scale: int = 1):
        if self._writer is not None:
            import numpy as np
            from PIL import Image
            frame = np.array(frame) if isinstance(frame, Image.Image) else frame
            self._last_img = frame
            self._writer.append_data(self.scale_image(img=np.array(frame), scale=scale, block_size=16))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._writer is not None:
            self._writer.close()
            self._log(f"Video rendered to \"{os.path.abspath(self._fname)}\"")
            if self._final_as_img and self._last_img is not None:
                from PIL import Image
                img = Image.fromarray(self._last_img)
                img.save(f"{self._fname}.png")
                self._log(f"Saved final frame of video to \"{self._fname}.png\"")

    # noinspection DuplicatedCode
    @staticmethod
    def scale_image(img: "np.ndarray", scale: int, block_size: int = 1) -> "np.ndarray":
        from PIL import Image
        import numpy as np
        new_size = np.array(list(reversed(img.shape[:2]))) * scale
        new_size = block_size * np.ceil(new_size / block_size).astype(int)
        img = Image.fromarray(img)
        img = img.resize(size=new_size, resample=Image.NEAREST)
        img = np.array(img)
        return img
