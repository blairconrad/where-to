import argparse
import colorsys
import ctypes
import datetime
import os
import sys
import tempfile
import win32com
import win32com.client

try:
    import Image
    import ImageDraw
    import ImageFont
except ImportError:
    try:
        from PIL import Image
        from PIL import ImageDraw
        from PIL import ImageFont
    except ImportError:
        raise Exception("Can't import PIL or PILLOW. Install one.")


def main(args=None):

    if sys.stdin:
        do_main(args)

    else:
        dir_name = os.path.join(tempfile.gettempdir(), "where-to")
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        console_outfile = os.path.join(dir_name, "output.txt")

        if os.path.exists(console_outfile):
            os.remove(console_outfile)

        sys.stderr = sys.stdout = open(console_outfile, "w")
        try:
            do_main(args)
        except Exception as e:
            print(e)
        finally:
            sys.stdout.flush()
            stats = os.stat(console_outfile)
            if stats.st_size > 0:
                os.system("notepad.exe " + console_outfile)


def do_main(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "which",
        metavar="which",
        default="upcoming",
        choices=["upcoming", "next", "now"],
        type=str,
        nargs="?",
        help="Which meetings to show.",
    )
    parser.add_argument(
        "--display-mode",
        metavar="mode",
        default="lock",
        choices=["list", "lock"],
        type=str,
        help="""How to show the meetings - paint on the lock screen or list to the console (which is
        only useful when a terminal is available, for example when invoked via the where-to-console
        executable).""",
    )
    parser.add_argument(
        "--background-color",
        metavar="color",
        type=str,
        help="""The background color to print messages on. Only useful in 'lock' mode. If both this
        option and --background-image are present, the background images will be overlaid on a field
        of this color before messages are printed.""",
    )

    parser.add_argument(
        "--background-image",
        metavar="FILE",
        type=str,
        help="The background to overlay messages on. Only useful in 'lock' mode.",
    )
    parser.add_argument("--now", type=datetime.datetime.fromisoformat, help=argparse.SUPPRESS)

    args = parser.parse_args(args)

    now = args.now if args.now else datetime.datetime.now()

    appointments = find_appointments(args.which, now)
    if args.display_mode == "list":
        if not appointments:
            print("No appointments found!")

        for appointment in appointments:
            print(appointment.Start, appointment.Subject, appointment.Location)
    else:
        screen_size = Windows.get_screen_size()
        lock_size = calculate_lock_size(screen_size)
        bottom_layer = create_bottom_layer(lock_size, args)
        image = create_image(appointments, bottom_layer, args)
        change_logon_background(image)


class Windows:
    SM_CXSCREEN = 0
    SM_CYSCREEN = 1

    @classmethod
    def get_screen_size(cls):
        width = ctypes.windll.user32.GetSystemMetrics(Windows.SM_CXSCREEN)
        height = ctypes.windll.user32.GetSystemMetrics(Windows.SM_CYSCREEN)
        return (width, height)

    @classmethod
    def is_windows_7(cls):
        windows_version = sys.getwindowsversion()
        return windows_version.major == 6 and windows_version.minor == 1

    class disable_file_system_redirection:
        _disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
        _revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection

        @classmethod
        def __enter__(self):
            self.old_value = ctypes.c_long()
            self.success = self._disable(ctypes.byref(self.old_value))

        @classmethod
        def __exit__(self, type, value, traceback):
            if self.success:
                self._revert(self.old_value)


def find_appointments(which, now):
    earliest_meeting_start = now + datetime.timedelta(minutes=-10)
    latest_meeting_start = datetime.datetime(year=now.year, month=now.month, day=now.day) + datetime.timedelta(days=1)

    if which == "now":
        latest_meeting_start = now + datetime.timedelta(minutes=15)

    OUTLOOK_FOLDER_CALENDAR = 9

    filter_early = datetime.datetime.strftime(earliest_meeting_start, "%Y-%m-%d %H:%M")
    filter_late = datetime.datetime.strftime(latest_meeting_start, "%Y-%m-%d %H:%M")

    filter = f"[MessageClass]='IPM.Appointment' AND [Start] >= '{filter_early}' AND [Start] <= '{filter_late}'"

    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    appointments = outlook.GetDefaultFolder(OUTLOOK_FOLDER_CALENDAR).Items
    appointments.IncludeRecurrences = True

    appointments = list(
        [
            appointment
            for appointment in resolve_recurring_appointments(appointments.Restrict(filter), now)
            if earliest_meeting_start <= appointment.Start.replace(tzinfo=None) <= latest_meeting_start
        ]
    )

    if which == "next":
        appointments = [a for a in appointments if a.Start == appointments[0].Start]

    return sorted(appointments, key=lambda a: a.Start)


def resolve_recurring_appointments(appointments, now):
    for appointment in appointments:
        if not appointment.IsRecurring:
            yield appointment

        try:
            filter = appointment.Start.replace(year=now.year, month=now.month, day=now.day)
            appointment = appointment.GetRecurrencePattern().GetOccurrence(filter)
            yield appointment
        except Exception:
            pass


def calculate_lock_size(screen_size):

    logon_screen_dimensions = [
        (1360, 768),
        (1280, 768),
        (1920, 1200),
        (1440, 900),
        (1600, 1200),
        (1280, 960),
        (1024, 768),
        (1280, 1024),
        (1024, 1280),
        (960, 1280),
        (900, 1440),
        (768, 1280),
    ]

    for possible_screen_size in logon_screen_dimensions:
        if possible_screen_size[0] * screen_size[1] == possible_screen_size[1] * screen_size[0]:
            return possible_screen_size

    return logon_screen_dimensions[0]


def create_bottom_layer(lock_size, config):
    i = Image.new("RGB", lock_size, config.background_color)

    if config.background_image:
        orig = Image.open(config.background_image)
        stamp = resize_to_fit(orig, lock_size)
        if stamp.size == lock_size:
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
        return image.resize(
            (int(container_size[1] * image.size[0] / image.size[1]), container_size[1]), Image.BILINEAR,
        )
    else:
        # image is fatter than container
        return image.resize(
            (container_size[0], int(container_size[0] * image.size[1] / image.size[0])), Image.BILINEAR,
        )


def create_image(appointments, background, config):
    if not appointments:
        return background

    font_size = 16
    font = ImageFont.truetype("verdana.ttf", font_size)

    messages = [
        datetime.datetime.strftime(appointment.Start, "%H:%M") + " " + appointment.Location
        for appointment in appointments
    ]

    draw = ImageDraw.Draw(background)
    sizes = [draw.textsize(message, font=font) for message in messages]

    max_width = max((size[0] for size in sizes))
    total_height = sum((size[1] for size in sizes))

    if config.background_image:
        overlay = Image.new("RGBA", (max_width, total_height), "#00000080")
        mask = overlay
        font_color = "white"
    else:
        overlay = Image.new("RGB", (max_width, total_height), config.background_color)
        mask = None
        font_color = get_font_color_from_pixel(overlay.getpixel((0, 0)))

    draw = ImageDraw.Draw(overlay)

    pos = (0, 0)
    for index in range(len(messages)):
        draw.text(pos, messages[index], font=font, fill=font_color)
        pos = (pos[0], pos[1] + sizes[index][1])

    background.paste(overlay, (background.size[0] - max_width, 0), mask)

    return background


def get_font_color_from_pixel(background_color):
    rgb = [c / 0xFF for c in background_color]
    hsv = colorsys.rgb_to_hsv(*rgb)
    h = hsv[0] + 0.5 if hsv[0] < 0.5 else hsv[0] - 0.5
    s = hsv[1]
    v = 1 if hsv[2] <= 0.5 else 0

    rgb = colorsys.hsv_to_rgb(h, s, v)
    rgb = "#" + hex(int(0xFF * rgb[0]))[2:] + hex(int(0xFF * rgb[1]))[2:] + hex(int(0xFF * rgb[2]))[2:]
    return rgb


def change_logon_background(image):
    # change the logon UI background if on Windows 7. From learning at
    # http://www.withinwindows.com/2009/03/15/windows-7-to-officially-support-logon-ui-background-customization/
    if not Windows.is_windows_7():
        print("not windows 7")
        return

    logon_background_dir = r"%(windir)s\system32\oobe\info\backgrounds" % os.environ

    if not os.path.exists(logon_background_dir):
        os.makedirs(logon_background_dir)

    logon_background_path = os.path.join(logon_background_dir, "background%dx%d.jpg" % image.size)
    quality = 80
    with Windows.disable_file_system_redirection():
        while quality > 0:
            image.save(logon_background_path, "JPEG", quality=quality)
            file_size = os.path.getsize(logon_background_path)
            if file_size < 256 * 1000:
                break
            quality -= 5


if __name__ == "__main__":
    main(sys.argv[1:])
