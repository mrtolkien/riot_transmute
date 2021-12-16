import json
import os
import pickle

# This here takes pro games from past years and tests parsing on each of them
import pytest

from riot_transmute import (
    match_to_game,
    match_timeline_to_game,
    merge_games_from_riot_match_and_timeline,
)

data_folder = os.path.join("tests", "data", "v4")

# The export folder is ignored in git and used to test packages relying on Riot Transmute
export_folder = os.path.join("tests", "data", "exports")

os.makedirs(export_folder, exist_ok=True)

version_files = [
    f for f in os.listdir(data_folder) if "source" not in f and f != "exports"
]


@pytest.mark.parametrize("input_file", version_files)
def test_parsing(input_file):
    with open(os.path.join(data_folder, input_file)) as file:
        raw = json.load(file)

    match_dto = raw["match"]
    timeline_dto = raw["timeline"]

    game = match_to_game(match_dto)
    game_timeline = match_timeline_to_game(timeline_dto, 0, "")

    merged_game = merge_games_from_riot_match_and_timeline(game, game_timeline)

    assert merged_game is not None

    with open(os.path.join(export_folder, input_file + ".pkl"), "wb+") as file:
        pickle.dump(merged_game, file)
