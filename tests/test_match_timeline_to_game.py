import json
import lol_dto.utilities
import os
import roleml

from riot_transmute.match_to_game import match_to_game
from riot_transmute.match_timeline_to_game import match_timeline_to_game


def test_timeline(timeline_game_id_platform_id):
    timeline, game_id, platform_id = timeline_game_id_platform_id

    game = match_timeline_to_game(timeline, game_id, platform_id)

    with open(os.path.join("examples", "game_from_timeline.json"), "w+") as file:
        json.dump(game, file, indent=4)

    assert game.sources.riotLolApi.gameId == game_id
    assert game.teams.BLUE.players[0].snapshots.__len__() > 0

    # TODO Test events individually


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
