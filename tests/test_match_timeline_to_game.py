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
    assert len(game.teams.BLUE.players[0].snapshots) > 0

    for kill in game.kills:
        assert kill.victimId is not None

    for team in game.teams:
        for player in team.players:
            for snapshot in player.snapshots:
                assert snapshot.timestamp is not None


def test_esports_timeline(esports_timeline):
    game = match_timeline_to_game(esports_timeline, 0, "")

    assert game
