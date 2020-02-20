import colorsys

from PIL import Image


def create_background(size, background_color, background_image):
    i = Image.new("RGB", size, background_color)

    if background_image:
        orig = Image.open(background_image)
        stamp = resize_to_fit(orig, size)
        if stamp.size == size:
            return stamp

        i.paste(stamp, (0, i.size[1] - stamp.size[1]))

    return i


def resize_to_fit(image, container_size):
    if image.size == container_size:
        return image

    if image.size[0] * container_size[1] == image.size[1] * container_size[0]:
        return image.resize(container_size, Image.BILINEAR)

    if image.size[0] / image.size[1] < container_size[0] / container_size[1]:
        # image is skinnier than container
        return image.resize((int(container_size[1] * image.size[0] / image.size[1]), container_size[1]), Image.BILINEAR)
    else:
        # image is fatter than container
        return image.resize((container_size[0], int(container_size[0] * image.size[1] / image.size[0])), Image.BILINEAR)


def get_best_font_color(image, region):
    def get_lightness_from_pixel(image, x, y):
        rgb = [c / 0xFF for c in image.getpixel((x, y))]
        return colorsys.rgb_to_hls(*rgb)[1]

    values = (
        get_lightness_from_pixel(image, x, y) for x in range(region[0], region[2]) for y in range(region[1], region[3])
    )
    first = next(values)
    if first < 0.5:
        for value in values:
            if value >= 0.5:
                return None
        return "white"
    else:
        for value in values:
            if value < 0.5:
                return None
        return "black"
