import os

import lol_dto
import roleml

from riot_transmute import match_to_game, match_timeline_to_game
from riot_transmute.merge_match_and_timeline import (
    merge_games_from_riot_match_and_timeline,
)


def test_full(match_v4_dto, timeline_game_id_platform_id):
    timeline, game_id, platform_id = timeline_game_id_platform_id

    match_dto, timeline = roleml.fix_game(
        match_v4_dto,
        timeline,
        True,
    )

    game_match = match_to_game(match_dto)
    game_timeline = match_timeline_to_game(timeline, game_id, platform_id)

    game_full = merge_games_from_riot_match_and_timeline(game_match, game_timeline)

    lol_dto.utilities.dump_json(game_full, os.path.join("examples", "game_merged.json"))

    assert game_full.sources.riotLolApi.gameId == game_id
    assert game_full.teams.BLUE.players[0].snapshots.__len__() > 0
    assert game_full.duration
    assert game_full.patch

    return game_full


def test_custom_game(custom_match_and_timeline):
    match, timeline = custom_match_and_timeline

    game = match_to_game(match)
    game_timeline = match_timeline_to_game(timeline, 4676184349, "EUW1")

    assert merge_games_from_riot_match_and_timeline(game, game_timeline)
