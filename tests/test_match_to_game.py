import os
import lol_dto.utilities
from riot_transmute import match_to_game


def test_game_v4(match_v4_dto):
    game = match_to_game(match_v4_dto)

    lol_dto.utilities.dump_json(game, os.path.join("examples", "game_from_match.json"))

    assert game.winner == "BLUE"
    assert game.patch == "10.10"
    assert game.start == "2020-05-26T17:23:02+00:00"
    assert hasattr(game.sources, "riotLolApi")
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


def test_esports_match(esports_match_dto):
    game = match_to_game(esports_match_dto)

    assert game


def test_game_v5(match_v5_dto):
    ...
