from where_to.application import Application

from .helpers import Appointment


def test_upcoming_appointments_are_sorted(config, mocker, capsys):
    expected_output = """
2020-02-20 08:30:00 [Subject] [Location]
2020-02-20 10:30:00 [Subject] [Location]
2020-02-20 12:00:00 [Subject] [Location]
""".lstrip()

    found_appointments = [
        Appointment(start="2020-02-20 12:00"),
        Appointment(start="2020-02-20 08:30"),
        Appointment(start="2020-02-20 10:30"),
    ]
    mocker.patch("where_to.outlook.find_appointments_between", return_value=found_appointments)
    application = Application(config)

    application.run()

    captured = capsys.readouterr()
    assert expected_output == captured.out


def test_next_appointment_shows_next_only(config, mocker, capsys):
    expected_output = """
2020-02-20 12:00:00 [Subject] [Location]
""".lstrip()

    found_appointments = [
        Appointment(start="2020-02-20 12:00"),
        Appointment(start="2020-02-20 13:30"),
        Appointment(start="2020-02-20 13:30"),
    ]
    mocker.patch("where_to.outlook.find_appointments_between", return_value=found_appointments)

    config.which = "next"
    application = Application(config)

    application.run()

    captured = capsys.readouterr()
    assert expected_output == captured.out


def test_next_appointment_shows_next_only_even_when_results_not_sorted(config, mocker, capsys):
    expected_output = """
2020-02-20 12:00:00 [Subject] [Location]
""".lstrip()

    found_appointments = [
        Appointment(start="2020-02-20 13:30"),
        Appointment(start="2020-02-20 12:00"),
        Appointment(start="2020-02-20 13:45"),
    ]
    mocker.patch("where_to.outlook.find_appointments_between", return_value=found_appointments)

    config.which = "next"
    application = Application(config)

    application.run()

    captured = capsys.readouterr()
    assert expected_output == captured.out


def test_next_appointment_shows_multiple_with_same_start(config, mocker, capsys):
    expected_output = """
2020-02-20 08:30:00 [Subject] [Location]
2020-02-20 08:30:00 [Subject] [Location]
""".lstrip()

    found_appointments = [
        Appointment(start="2020-02-20 08:30"),
        Appointment(start="2020-02-20 08:30"),
        Appointment(start="2020-02-20 12:00"),
    ]
    mocker.patch("where_to.outlook.find_appointments_between", return_value=found_appointments)

    config.which = "next"
    application = Application(config)

    application.run()

    captured = capsys.readouterr()
    assert expected_output == captured.out
