import json

import lol_dto
import pytest
import os

from riotwatcher import LolWatcher
from riot_api_to_lol_dto.match_to_game import match_to_game
from riot_api_to_lol_dto.match_timeline_to_game import match_timeline_to_game


@pytest.fixture
def watcher():
    with open(os.path.join(os.path.expanduser("~"), ".config", "riot", "api_key.txt")) as file:
        api_key = file.read()
    return LolWatcher(api_key)


@pytest.fixture
def match_dto(watcher):
    match_dto = watcher.match.by_id("KR", 4409190456)
    with open(os.path.join('examples', 'match.json'), 'w+') as file:
        json.dump(match_dto, file, indent=4)
    return match_dto


@pytest.fixture
def timeline_game_id_platform_id(watcher):
    timeline = watcher.match.timeline_by_match("KR", 4409190456), 4409190456, "KR"
    with open(os.path.join('examples', 'match_timeline.json'), 'w+') as file:
        json.dump(timeline, file, indent=4)
    return timeline


def test_game(match_dto):
    game = match_to_game(match_dto)

    with open(os.path.join('examples', 'game_from_match.json'), 'w+') as file:
        json.dump(game, file, indent=4)

    assert game["winner"] == "blue"
    assert game["patch"] == "10.10"
    assert game["startDate"] == "2020-05-27T02:23:02.536000"
    assert "riot" in game["sources"]
    assert game["teams"]["blue"]["firstTower"]
    assert not game["teams"]["blue"]["firstDragon"]
    assert game["teams"]["blue"]["bans"].__len__() == 5
    assert game["teams"]["blue"]["players"].__len__() == 5

    onfleek = next(
        p for p in game["teams"]["blue"]["players"] if p["inGameName"] == "SANDBOX OnFleek"
    )

    assert "riot" in onfleek["foreignKeys"]
    assert onfleek["runes"]["primaryTreeId"] == 8000
    assert onfleek["items"][0]["id"] == 3047


def test_timeline(timeline_game_id_platform_id):
    timeline, game_id, platform_id = timeline_game_id_platform_id

    game = match_timeline_to_game(timeline, game_id, platform_id)

    with open(os.path.join('examples', 'game_from_match_timeline.json'), 'w+') as file:
        json.dump(game, file, indent=4)

    assert game['sources']['riot']['gameId'] == game_id

    assert game['teams']['blue']['players'][0]['snapshots'].__len__() > 0


def test_both(match_dto, timeline_game_id_platform_id):
    pass
