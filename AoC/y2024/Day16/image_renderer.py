from typing import Tuple, TypeVar, Callable, Optional

T = TypeVar('T')
DRAWELEMENTTYPE = Callable[
    ["ImageDraw", T, Tuple[Tuple[int, int], Tuple[int, int]], Tuple[int, int], Tuple[int, int, int]], None]


def default_draw_element(
        draw: "ImageDraw", el, xy: Tuple[Tuple[int, int], Tuple[int, int]], pos: Tuple[int, int],
        color: Tuple[int, int, int]
) -> None:
    (x_min, y_min), (x_max, y_max) = xy
    draw.rectangle(xy=(x_min + 1, y_min + 1, x_max - 1, y_max - 1), fill=color, outline=color, width=1)


def draw_frame(
        pixel_size: int, header: str, size: Tuple[int, int],
        get_element: Callable[[Tuple[int, int]], T],
        pixel_color: Callable[[T], Tuple[int, int, int]],
        bg_color: Tuple[int, int, int] = (0, 0, 0), heading_color: Tuple[int, int, int] = (127, 131, 134),
        draw_element: DRAWELEMENTTYPE = default_draw_element,
        heading_size: Optional[int] = None, border_size: int = 1, font=None,
):
    from PIL import Image, ImageDraw, ImageFont
    header = "" if header is None else header

    heading_size = (pixel_size * 2 if heading_size is None else heading_size) if len(header) > 0 else 0

    # (y_min, y_max), (x_min, x_max) = self.get_bounds()
    width, height = size

    ret = Image.new("RGB",
                    ((width + (2 * border_size)) * pixel_size,
                     (height + (3 * border_size)) * pixel_size + heading_size),
                    bg_color)
    draw = ImageDraw.Draw(ret)

    font = ImageFont.truetype(font="cour.ttf", size=heading_size) if font is None else font
    if heading_size > 0:
        draw.text((pixel_size * (width / 2 + 0.5), pixel_size),
                  header, heading_color, font, align="center", anchor="mt")

    for x in range(width):
        for y in range(height):
            pixel_x, pixel_y = (x + (1 * border_size)) * pixel_size, (y + (2 * border_size)) * pixel_size + heading_size
            el = get_element((x, y))
            color = pixel_color(el)
            if color is not None:
                draw_element(draw, el, ((pixel_x, pixel_y), (pixel_x + pixel_size, pixel_y + pixel_size)), (x, y),
                             color)
    return ret
