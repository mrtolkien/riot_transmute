import json
import os

import pytest
from riotwatcher import LolWatcher
import dotenv

dotenv.load_dotenv()


# Relic of the past, could be removed
@pytest.fixture
def watcher():
    return LolWatcher(os.environ["RIOT_API_KEY"])


@pytest.fixture
def match_dto(watcher):
    file_location = os.path.join(os.getcwd(), "examples", "source_match.json")

    # match_dto = watcher.match.by_id("KR", 4409190456)

    with open(file_location) as file:
        match_dto = json.load(file)

    return match_dto


@pytest.fixture
def timeline_game_id_platform_id(watcher):
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
