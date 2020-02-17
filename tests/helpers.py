from datetime import datetime


class Appointment:
    def __init__(self, start, subject="[Subject]", location="[Location]"):
        self.Start = datetime.fromisoformat(start)
        self.Subject = subject
        self.Location = location
