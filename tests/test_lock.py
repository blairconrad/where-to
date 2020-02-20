import os
import pytest

from PIL import Image
from PIL import ImageChops
from pathlib import Path

from where_to.application import Application

from .helpers import Appointment


@pytest.fixture
def mocker(mocker, request):
    mocker.patch("where_to.lock_screen.get_best_size", return_value=(800, 600))
    mocker.patch("where_to.lock_screen.show", side_effect=CompareImage(request))
    return mocker


@pytest.fixture
def config(config):
    config.display_mode = "lock"
    return config


def test_single_appointment_default_background_writes_white_on_black(config, mocker):
    found_appointments = [Appointment(start="2020-02-20 12:00")]
    mocker.patch("where_to.outlook.find_appointments_between", return_value=found_appointments)
    application = Application(config)

    application.run()


def test_single_appointment_yellow_background_writes_black_on_yellow(config, mocker):
    found_appointments = [Appointment(start="2020-02-20 12:00")]
    mocker.patch("where_to.outlook.find_appointments_between", return_value=found_appointments)
    config.background_color = "yellow"
    application = Application(config)

    application.run()


def test_single_appointment_checkered_background_writes_white_on_smoke(config, mocker, request):
    found_appointments = [Appointment(start="2020-02-20 12:00")]
    mocker.patch("where_to.outlook.find_appointments_between", return_value=found_appointments)

    config.background_image = os.path.abspath(
        os.path.join(os.path.dirname(request.fspath), "backgrounds", "black_and_white_checkered.png")
    )
    application = Application(config)

    application.run()


def test_single_appointment_light_checkered_background_writes_black(config, mocker, request):
    found_appointments = [Appointment(start="2020-02-20 12:00")]
    mocker.patch("where_to.outlook.find_appointments_between", return_value=found_appointments)

    config.background_image = os.path.abspath(
        os.path.join(os.path.dirname(request.fspath), "backgrounds", "yellow_and_white_checkered.png")
    )
    application = Application(config)

    application.run()


def test_single_appointment_dark_checkered_background_writes_white(config, mocker, request):
    found_appointments = [Appointment(start="2020-02-20 12:00")]
    mocker.patch("where_to.outlook.find_appointments_between", return_value=found_appointments)

    config.background_image = os.path.abspath(
        os.path.join(os.path.dirname(request.fspath), "backgrounds", "black_and_navy_checkered.png")
    )
    application = Application(config)

    application.run()


class CompareImage:
    def __init__(self, request):
        self.image_base = request.node.name
        self.test_dir = os.path.dirname(request.fspath)
        self.test_output_dir = os.path.abspath(os.path.join(self.test_dir, "..", "test_output"))

    def __call__(self, lock_image):
        actual_path = os.path.join(self.test_output_dir, self.image_base + ".actual.png")
        difference_path = os.path.join(self.test_output_dir, self.image_base + ".difference.png")

        if os.path.exists(actual_path):
            os.remove(actual_path)
        if os.path.exists(difference_path):
            os.remove(difference_path)

        expected_path = os.path.join(self.test_dir, "expected", self.image_base + ".png")
        expected_image = Image.open(expected_path)

        difference = ImageChops.difference(lock_image, expected_image)

        if difference.getbbox() is not None:
            Path(self.test_output_dir).mkdir(parents=True, exist_ok=True)

            lock_image.save(actual_path)
            difference.save(difference_path)

            assert (
                False
            ), f"Images differ. Compare {actual_path} and {expected_path}, or see differences in {difference_path}"
