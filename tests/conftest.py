import argparse
import pytest


@pytest.fixture
def config():
    config = argparse.Namespace()

    config.now = None
    config.which = "upcoming"
    config.display_mode = "list"
    config.background_color = None
    config.background_image = None

    return config
