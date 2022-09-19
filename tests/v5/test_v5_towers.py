"""Testing tower data creation.

The tower data changed format from 12.14 to 12.15 and needed checking.
"""
from lol_dto.classes import game

import riot_transmute
from tests import conftest


def get_merged_game(filename: str) -> game.LolGame:
    match = conftest.load_json("v4", f"{filename}.json")
    timeline = conftest.load_json("v4", f"{filename}_timeline.json")

    lol_game = riot_transmute.v5.match_to_game(match)
    lol_game_timeline = riot_transmute.v5.match_timeline_to_game(timeline)

    return riot_transmute.merge_games_from_riot_match_and_timeline(
        lol_game, lol_game_timeline
    )


def test_12_14():
    """Testing 12.14 game: ESPORTSTMNT03_2961931
    https://www.youtube.com/watch?v=K2BZKorXGi4
    """
    lol_game = get_merged_game("ESPORTSTMNT03_2961931")

    # TODO Check vod
    assert lol_game.winner == ...


def test_12_15():
    """Testing 12.15 game: ESPORTSTMNT01_3096461
    https://www.youtube.com/watch?v=i34uceAGw0I
    """
    lol_game = get_merged_game("ESPORTSTMNT01_3096461")

    # TODO Check vod
    assert lol_game.winner == ...
