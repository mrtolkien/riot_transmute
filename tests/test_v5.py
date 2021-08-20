import json
import os

import pytest

import riot_transmute


data_folder = os.path.join("tests", "data", "v5")


# Testing a single game against specific values
def test_match_to_game_v5():
    with open(os.path.join(data_folder, f"match_v5_ranked.json")) as file:
        match_dto = json.load(file)["info"]

    game = riot_transmute.match_to_game(match_dto, match_v5=True)

    assert game.winner == "RED"
    assert game.patch == "11.16"
    assert game.type == "MATCHED_GAME"
