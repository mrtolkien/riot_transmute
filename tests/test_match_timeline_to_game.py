import json
import lol_dto.utilities
import os

from riot_transmute.match_timeline_to_game import match_timeline_to_game


def test_timeline(timeline_game_id_platform_id):
    timeline, game_id, platform_id = timeline_game_id_platform_id

    game = match_timeline_to_game(timeline, game_id, platform_id)

    lol_dto.utilities.dump_json(
        game, os.path.join("examples", "game_from_timeline.json")
    )

    assert game.sources.riotLolApi.gameId == game_id
    assert game.teams.BLUE.players[0].snapshots.__len__() > 0

    # TODO Test events individually


def test_timeline_with_names(timeline_game_id_platform_id):
    timeline, game_id, platform_id = timeline_game_id_platform_id

    game = match_timeline_to_game(timeline, game_id, platform_id, add_names=True)

    lol_dto.utilities.dump_json(
        game, os.path.join("examples", "game_from_timeline_with_names.json")
    )

    for p in game.teams.BLUE.players:
        for event in p.itemsEvents:
            assert event.name is not None


def test_esports_timeline():
    with open(os.path.join("examples", "source_timeline_esports.json")) as file:
        match_dto = json.load(file)

    game = match_timeline_to_game(match_dto, 0, "")

    assert game
