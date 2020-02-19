import datetime

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from . import image
from . import lock_screen
from . import outlook


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
                print(appointment.Start, appointment.Location)
        else:
            lock_size = lock_screen.get_best_size()
            bottom_layer = image.create_background(
                lock_size, self.config.background_color, self.config.background_image
            )
            lock_image = self.create_image(appointments, bottom_layer)
            lock_screen.show(lock_image)

    def find_appointments(self):
        def distinct(appointments):
            result = []
            for appointment in appointments:
                if result and result[-1].Start == appointment.Start and result[-1].Location == appointment.Location:
                    continue
                result.append(appointment)
            return result

        earliest_meeting_start = self.now + datetime.timedelta(minutes=-10)
        latest_meeting_start = datetime.datetime(
            year=self.now.year, month=self.now.month, day=self.now.day
        ) + datetime.timedelta(days=1)

        if self.config.which == "now":
            latest_meeting_start = self.now + datetime.timedelta(minutes=15)

        appointments = outlook.find_appointments_between(earliest_meeting_start, latest_meeting_start)
        appointments = distinct(sorted(appointments, key=lambda a: a.Start))

        if self.config.which == "next":
            appointments = [a for a in appointments if a.Start == appointments[0].Start]

        return appointments

    def create_image(self, appointments, background):
        if not appointments:
            return background

        font = ImageFont.truetype("verdana.ttf", size=16)

        message = "\n".join(
            (
                datetime.datetime.strftime(appointment.Start, "%H:%M") + " " + appointment.Location
                for appointment in appointments
            )
        )

        draw = ImageDraw.Draw(background)
        message_size = draw.textsize(message, font)

        if self.config.background_image:
            overlay = Image.new("RGBA", message_size, "#00000080")
            mask = overlay
            font_color = "white"
        else:
            overlay = Image.new("RGB", message_size, self.config.background_color)
            mask = None
            font_color = image.get_font_color_from_pixel(overlay.getpixel((0, 0)))

        draw = ImageDraw.Draw(overlay)

        pos = (0, 0)
        draw.text(pos, message, font=font, fill=font_color)

        background.paste(overlay, (background.size[0] - message_size[0], 0), mask)

        return background
