import json
import os

import pytest
import dotenv

dotenv.load_dotenv()


@pytest.fixture
def match_v4_dto():
    file_location = os.path.join("tests", "data", "v4", "source_match.json")

    with open(file_location) as file:
        match_dto = json.load(file)

    return match_dto


@pytest.fixture
def timeline_game_id_platform_id():
    file_location = os.path.join("tests", "data", "v4", "source_timeline.json")

    with open(file_location) as file:
        timeline_game_platform = json.load(file)

    return timeline_game_platform, 4409190456, "KR"


@pytest.fixture
def esports_match_dto():
    with open(os.path.join("tests", "data", "v4", "source_match_esports.json")) as file:
        match_dto = json.load(file)

    return match_dto


@pytest.fixture()
def esports_timeline():
    with open(
        os.path.join("tests", "data", "v4", "source_timeline_esports.json")
    ) as file:
        match_dto = json.load(file)

    return match_dto


@pytest.fixture
def custom_match_and_timeline():
    with open(os.path.join("tests", "data", "v4", "source_custom.json")) as file:
        match = json.load(file)

    with open(
        os.path.join("tests", "data", "v4", "source_custom_timeline.json")
    ) as file:
        timeline = json.load(file)

    return match, timeline
