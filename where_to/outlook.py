import datetime
import win32com.client


def find_appointments_between(earliest_meeting_start, latest_meeting_start):
    OUTLOOK_FOLDER_CALENDAR = 9

    filter_early = datetime.datetime.strftime(earliest_meeting_start, "%Y-%m-%d %H:%M")
    filter_late = datetime.datetime.strftime(latest_meeting_start, "%Y-%m-%d %H:%M")

    filter = f"[MessageClass]='IPM.Appointment' AND [Start] >= '{filter_early}' AND [Start] <= '{filter_late}'"

    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    appointments = outlook.GetDefaultFolder(OUTLOOK_FOLDER_CALENDAR).Items
    appointments.IncludeRecurrences = True

    return list(
        [
            appointment
            for appointment in resolve_recurring_appointments(
                appointments.Restrict(filter), earliest_meeting_start, latest_meeting_start
            )
            if earliest_meeting_start <= appointment.Start.replace(tzinfo=None) <= latest_meeting_start
        ]
    )


def resolve_recurring_appointments(appointments, earliest_meeting_start, latest_meeting_start):
    meeting_days = set()
    latest_day = latest_meeting_start.date()
    day = earliest_meeting_start.date()

    while day <= latest_day:
        meeting_days.add(day)
        day += datetime.timedelta(days=1)

    for appointment in appointments:
        if not appointment.IsRecurring:
            yield appointment

        recurrences = appointment.GetRecurrencePattern()

        for day in meeting_days:
            try:
                filter = appointment.Start.replace(year=day.year, month=day.month, day=day.day)
                yield recurrences.GetOccurrence(filter)
            except Exception:
                pass

        for exception in recurrences.Exceptions:
            if not exception.Deleted:
                yield exception.AppointmentItem
