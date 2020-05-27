import lol_dto
import pytest
import os

from riotwatcher_dto.match_dto_to_game import match_dto_to_game
from riotwatcher_dto.riotwatcher_dto import LolWatcherDto


@pytest.fixture
def watcher_dto():
    with open(os.path.join(os.path.expanduser("~"), ".config", "riot", "api_key.txt")) as file:
        api_key = file.read()
    return LolWatcherDto(api_key)


@pytest.fixture
def match_dto(watcher_dto) -> lol_dto.LolGame:
    return watcher_dto.match.by_id("KR", 4409190456)


@pytest.fixture
def timeline(watcher_dto) -> lol_dto.LolGame:
    return watcher_dto.match.timeline_by_match("KR", 4409190456)


def test_game(match_dto):
    game = match_dto_to_game(match_dto)
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


def test_timeline(timeline):
    pass


def test_both(match_dto, timeline):
    pass
