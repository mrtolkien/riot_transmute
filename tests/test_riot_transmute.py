import json
import lol_dto.utilities
import pytest
import os

from riotwatcher import LolWatcher
import roleml

from riot_transmute.match_to_game import match_to_game
from riot_transmute.match_timeline_to_game import match_timeline_to_game


@pytest.fixture
def watcher():
    return LolWatcher(os.environ["RIOT_API_KEY"])


@pytest.fixture
def match_dto(watcher):
    match_dto = watcher.match.by_id("KR", 4409190456)

    lol_dto.utilities.dump_json(
        match_dto,
        os.path.join("examples", "source_match.json"),
    )

    return match_dto


@pytest.fixture
def timeline_game_id_platform_id(watcher):
    timeline_game_platform = (
        watcher.match.timeline_by_match("KR", 4409190456),
        4409190456,
        "KR",
    )

    lol_dto.utilities.dump_json(
        timeline_game_platform[0],
        os.path.join("examples", "source_timeline.json"),
    )

    return timeline_game_platform


def test_game(match_dto):
    game = match_to_game(match_dto)

    with open(os.path.join("examples", "game_from_match.json"), "w+") as file:
        json.dump(game, file, indent=4)

    assert game.winner == "BLUE"
    assert game.patch == "10.10"
    assert game.start == "2020-05-26T17:23:02+00:00"
    assert "riotLolApi" in game.sources
    assert game.teams.BLUE.endOfGameStats.firstTurret is True
    assert game.teams.BLUE.endOfGameStats.firstDragon is False
    assert game.teams.BLUE.bans.__len__() == 5
    assert game.teams.BLUE.players.__len__() == 5

    onfleek = next(
        p for p in game.teams.BLUE.players if p.inGameName == "SANDBOX OnFleek"
    )

    assert hasattr(onfleek.sources, "riotLolApi")
    assert onfleek.primaryRuneTreeId == 8000
    assert onfleek.endOfGameStats.items[0].id == 3047


def test_game_with_names(match_dto):
    game = match_to_game(match_dto, add_names=True)

    lol_dto.utilities.dump_json(
        game,
        os.path.join("examples", "game_from_match_with_names.json"),
    )

    for p in game.teams.BLUE.players:
        assert p.championName is not None


def test_timeline(timeline_game_id_platform_id):
    timeline, game_id, platform_id = timeline_game_id_platform_id

    game = match_timeline_to_game(timeline, game_id, platform_id)

    with open(os.path.join("examples", "game_from_timeline.json"), "w+") as file:
        json.dump(game, file, indent=4)

    assert game.sources.riotLolApi.gameId == game_id
    assert game.teams.BLUE.players[0].snapshots.__len__() > 0

    # TODO Test events


def test_timeline_with_names(timeline_game_id_platform_id):
    timeline, game_id, platform_id = timeline_game_id_platform_id

    game = match_timeline_to_game(timeline, game_id, platform_id, add_names=True)

    with open(
        os.path.join("examples", "game_from_timeline_with_names.json"), "w+"
    ) as file:
        json.dump(game, file, indent=4)

    for p in game.teams.BLUE.players:
        for event in p.itemsEvents:
            assert event.name is not None


def test_full(match_dto, timeline_game_id_platform_id):
    timeline, game_id, platform_id = timeline_game_id_platform_id

    match_dto, timeline = roleml.fix_game(
        match_dto,
        timeline,
        True,
    )

    game_match = match_to_game(match_dto)
    game_timeline = match_timeline_to_game(timeline, game_id, platform_id)

    game_full = lol_dto.utilities.merge_games(game_match, game_timeline)

    with open(os.path.join("examples", "game_merged.json"), "w+") as file:
        json.dump(game_full, file, indent=4)

    assert game_full.sources.riotLolApi.gameId == game_id
    assert game_full.teams.BLUE.players[0].snapshots.__len__() > 0
    assert game_full.duration
    assert game_full.patch

    return game_full


def test_full_with_names(match_dto, timeline_game_id_platform_id):
    timeline, game_id, platform_id = timeline_game_id_platform_id

    game_match = match_to_game(match_dto, add_names=True)
    game_timeline = match_timeline_to_game(
        timeline, game_id, platform_id, add_names=True
    )

    game = lol_dto.utilities.merge_games(game_match, game_timeline)

    with open(os.path.join("examples", "game_merged_with_names.json"), "w+") as file:
        json.dump(game, file, indent=4)

    for p in game.teams.BLUE.players:
        assert p.championName is not None

        for event in p.itemsEvents:
            assert event.name is not None


def test_esports_match():
    with open(os.path.join("examples", "source_match_esports.json")) as file:
        match_dto = json.load(file)

    game = match_to_game(match_dto)

    assert game


def test_esports_timeline():
    with open(os.path.join("examples", "source_timeline_esports.json")) as file:
        match_dto = json.load(file)

    game = match_timeline_to_game(match_dto, 0, "")

    assert game


def test_custom_game(watcher):
    match = watcher.match.by_id("EUW1", 4676184349)
    timeline = watcher.match.timeline_by_match("EUW1", 4676184349)

    game = match_to_game(match, True)
    game_timeline = match_timeline_to_game(timeline, 4676184349, "EUW1", True)

    # TODO This should not be there anymore
    assert lol_dto.utilities.merge_games(game, game_timeline)
