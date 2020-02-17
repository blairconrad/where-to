from datetime import datetime


class Appointment:
    def __init__(self, start, subject="[Subject]", location="[Location]"):
        self.Start = datetime.fromisoformat(start)
        self.Subject = subject
        self.Location = location


def console(*lines):
    return "\n".join(lines) + "\n"
