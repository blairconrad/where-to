import colorsys
import datetime
import os
import win32com
import win32com.client

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from .windows import Windows


class Application:
    def __init__(self, config):
        self.config = config

    def run(self):
        self.now = self.config.now if self.config.now else datetime.datetime.now()

        appointments = self.find_appointments()
        if self.config.display_mode == "list":
            if not appointments:
                print("No appointments found!")

            for appointment in appointments:
                print(appointment.Start, appointment.Subject, appointment.Location)
        else:
            screen_size = Windows.get_screen_size()
            lock_size = self.calculate_lock_size(screen_size)
            bottom_layer = self.create_bottom_layer(lock_size)
            image = self.create_image(appointments, bottom_layer)
            self.change_logon_background(image)

    def find_appointments(self):
        earliest_meeting_start = self.now + datetime.timedelta(minutes=-10)
        latest_meeting_start = datetime.datetime(
            year=self.now.year, month=self.now.month, day=self.now.day
        ) + datetime.timedelta(days=1)

        if self.config.which == "now":
            latest_meeting_start = self.now + datetime.timedelta(minutes=15)

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
                for appointment in self.resolve_recurring_appointments(appointments.Restrict(filter))
                if earliest_meeting_start <= appointment.Start.replace(tzinfo=None) <= latest_meeting_start
            ]
        )

        if self.config.which == "next":
            appointments = [a for a in appointments if a.Start == appointments[0].Start]

        return sorted(appointments, key=lambda a: a.Start)

    def resolve_recurring_appointments(self, appointments):
        for appointment in appointments:
            if not appointment.IsRecurring:
                yield appointment

            try:
                filter = appointment.Start.replace(year=self.now.year, month=self.now.month, day=self.now.day)
                yield appointment.GetRecurrencePattern().GetOccurrence(filter)
            except Exception:
                pass

    def calculate_lock_size(self, screen_size):

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

    def create_bottom_layer(self, lock_size):
        i = Image.new("RGB", lock_size, self.config.background_color)

        if self.config.background_image:
            orig = Image.open(self.config.background_image)
            stamp = self.resize_to_fit(orig, lock_size)
            if stamp.size == lock_size:
                return stamp

            i.paste(stamp, (0, i.size[1] - stamp.size[1]))

        return i

    def resize_to_fit(self, image, container_size):
        if image.size == container_size:
            return image

        if image.size[0] * container_size[1] == image.size[1] * container_size[0]:
            return image.resize(container_size, Image.BILINEAR)

        if image.size[0] / image.size[1] < container_size[0] / container_size[1]:
            # image is skinnier than container
            return image.resize(
                (int(container_size[1] * image.size[0] / image.size[1]), container_size[1]), Image.BILINEAR
            )
        else:
            # image is fatter than container
            return image.resize(
                (container_size[0], int(container_size[0] * image.size[1] / image.size[0])), Image.BILINEAR
            )

    def create_image(self, appointments, background):
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

        if self.config.background_image:
            overlay = Image.new("RGBA", (max_width, total_height), "#00000080")
            mask = overlay
            font_color = "white"
        else:
            overlay = Image.new("RGB", (max_width, total_height), self.config.background_color)
            mask = None
            font_color = self.get_font_color_from_pixel(overlay.getpixel((0, 0)))

        draw = ImageDraw.Draw(overlay)

        pos = (0, 0)
        for index in range(len(messages)):
            draw.text(pos, messages[index], font=font, fill=font_color)
            pos = (pos[0], pos[1] + sizes[index][1])

        background.paste(overlay, (background.size[0] - max_width, 0), mask)

        return background

    def get_font_color_from_pixel(self, background_color):
        rgb = [c / 0xFF for c in background_color]
        hsv = colorsys.rgb_to_hsv(*rgb)
        h = hsv[0] + 0.5 if hsv[0] < 0.5 else hsv[0] - 0.5
        s = hsv[1]
        v = 1 if hsv[2] <= 0.5 else 0

        rgb = colorsys.hsv_to_rgb(h, s, v)
        rgb = "#" + hex(int(0xFF * rgb[0]))[2:] + hex(int(0xFF * rgb[1]))[2:] + hex(int(0xFF * rgb[2]))[2:]
        return rgb

    def change_logon_background(self, image):
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
