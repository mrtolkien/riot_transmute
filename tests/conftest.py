import json
import os

import pytest
from riotwatcher import LolWatcher
import dotenv

dotenv.load_dotenv()


# Relic of the past, could be removed
# @pytest.fixture
# def watcher():
#     return LolWatcher(os.environ["RIOT_API_KEY"])


@pytest.fixture
def match_dto():
    file_location = os.path.join(os.getcwd(), "examples", "source_match.json")

    # match_dto = watcher.match.by_id("KR", 4409190456)

    with open(file_location) as file:
        match_dto = json.load(file)

    return match_dto


@pytest.fixture
def timeline_game_id_platform_id():
    file_location = os.path.join("examples", "source_timeline.json")

    # timeline_game_platform = (
    #     watcher.match.timeline_by_match("KR", 4409190456),
    #     4409190456,
    #     "KR",
    # )

    with open(file_location) as file:
        timeline_game_platform = json.load(file)

    return timeline_game_platform, 4409190456, "KR"


@pytest.fixture
def esports_match_dto():
    with open(os.path.join("examples", "source_match_esports.json")) as file:
        match_dto = json.load(file)

    return match_dto


@pytest.fixture
def custom_match_and_timeline():
    # match = watcher.match.by_id("EUW1", 4676184349)
    # timeline = watcher.match.timeline_by_match("EUW1", 4676184349)

    with open(os.path.join("examples", "source_custom.json")) as file:
        match = json.load(file)

    with open(os.path.join("examples", "source_custom_timeline.json")) as file:
        timeline = json.load(file)

    return match, timeline
