"""Pytest defaults.
"""

import json
import os

import dotenv
import pytest

dotenv.load_dotenv()


def load_game(*args) -> dict:
    file_location = os.path.join(*args)

    with open(file_location, encoding="utf-8") as file:
        match_dto = json.load(file)

    return match_dto


@pytest.fixture
def match_v4_dto():
    return load_game("tests", "data", "v4", "source_match.json")


@pytest.fixture
def timeline_game_id_platform_id():
    return load_game("tests", "data", "v4", "source_timeline.json"), 4409190456, "KR"


@pytest.fixture
def esports_match_dto():
    return load_game("tests", "data", "v4", "source_match_esports.json")


@pytest.fixture()
def esports_timeline():
    return load_game("tests", "data", "v4", "source_timeline_esports.json")


@pytest.fixture
def custom_match_and_timeline():
    return load_game("tests", "data", "v4", "source_custom.json"), load_game(
        "tests", "data", "v4", "source_custom_timeline.json"
    )
