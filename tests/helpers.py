from datetime import datetime


class Appointment:
    def __init__(self, start, location="[Location]"):
        self.Start = datetime.fromisoformat(start)
        self.Location = location


def console(*lines):
    return "\n".join(lines) + "\n"
