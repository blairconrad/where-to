import datetime
import os

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from . import image
from . import outlook
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
            bottom_layer = image.create_background(
                lock_size, self.config.background_color, self.config.background_image
            )
            lock_image = self.create_image(appointments, bottom_layer)
            self.change_lock_screen(lock_image)

    def find_appointments(self):
        earliest_meeting_start = self.now + datetime.timedelta(minutes=-10)
        latest_meeting_start = datetime.datetime(
            year=self.now.year, month=self.now.month, day=self.now.day
        ) + datetime.timedelta(days=1)

        if self.config.which == "now":
            latest_meeting_start = self.now + datetime.timedelta(minutes=15)

        appointments = outlook.find_appointments_between(earliest_meeting_start, latest_meeting_start)

        if self.config.which == "next":
            appointments = [a for a in appointments if a.Start == appointments[0].Start]

        return sorted(appointments, key=lambda a: a.Start)

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
            font_color = image.get_font_color_from_pixel(overlay.getpixel((0, 0)))

        draw = ImageDraw.Draw(overlay)

        pos = (0, 0)
        for index in range(len(messages)):
            draw.text(pos, messages[index], font=font, fill=font_color)
            pos = (pos[0], pos[1] + sizes[index][1])

        background.paste(overlay, (background.size[0] - max_width, 0), mask)

        return background

    def change_lock_screen(self, lock_image):
        # change the logon UI background if on Windows 7. From learning at
        # http://www.withinwindows.com/2009/03/15/windows-7-to-officially-support-logon-ui-background-customization/
        if not Windows.is_windows_7():
            print("not windows 7")
            return

        logon_background_dir = r"%(windir)s\system32\oobe\info\backgrounds" % os.environ

        if not os.path.exists(logon_background_dir):
            os.makedirs(logon_background_dir)

        logon_background_path = os.path.join(logon_background_dir, "background%dx%d.jpg" % lock_image.size)
        quality = 80
        with Windows.disable_file_system_redirection():
            while quality > 0:
                lock_image.save(logon_background_path, "JPEG", quality=quality)
                file_size = os.path.getsize(logon_background_path)
                if file_size < 256 * 1000:
                    break
                quality -= 5
