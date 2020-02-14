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
            for appointment in resolve_recurring_appointments(appointments.Restrict(filter), earliest_meeting_start)
            if earliest_meeting_start <= appointment.Start.replace(tzinfo=None) <= latest_meeting_start
        ]
    )


def resolve_recurring_appointments(appointments, today):
    for appointment in appointments:
        if not appointment.IsRecurring:
            yield appointment

        recurrences = appointment.GetRecurrencePattern()

        try:
            filter = appointment.Start.replace(year=today.year, month=today.month, day=today.day)
            yield recurrences.GetOccurrence(filter)
        except Exception:
            pass

        for exception in recurrences.Exceptions:
            if not exception.Deleted:
                yield exception.AppointmentItem
