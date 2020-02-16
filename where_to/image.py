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


def get_font_color_from_pixel(background_color):
    rgb = [c / 0xFF for c in background_color]
    hsv = colorsys.rgb_to_hsv(*rgb)
    h = hsv[0] + 0.5 if hsv[0] < 0.5 else hsv[0] - 0.5
    s = hsv[1]
    v = 1 if hsv[2] <= 0.5 else 0

    rgb = colorsys.hsv_to_rgb(h, s, v)
    rgb = "#" + hex(int(0xFF * rgb[0]))[2:] + hex(int(0xFF * rgb[1]))[2:] + hex(int(0xFF * rgb[2]))[2:]
    return rgb
