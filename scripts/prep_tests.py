"""Small test files prep script.
"""

import json
import os

dump_folder = "C:\\Users\\garym\\Dev\\closed_source\\acs_dump\\dump"

files = os.listdir(dump_folder)

test_games = {}

for idx, f in enumerate(files):
    if idx % 100 == 0:
        print(idx)

    if "MatchDto" not in f:
        continue

    with open(os.path.join(dump_folder, f), encoding="utf-8") as file:
        match_dto = json.load(file)

    if "gameVersion" not in match_dto:
        print(f)
        continue

    if match_dto["gameVersion"] not in test_games:
        test_games[match_dto["gameVersion"]] = f

examples_folder = "C:\\Users\\garym\\Dev\\closed_source\\riot_transmute\\tests\\data"

for game_version, game_path in test_games.items():
    with open(
        os.path.join(dump_folder, game_path),
        encoding="utf-8",
    ) as file:
        match_dto = json.load(file)

    with open(
        os.path.join(
            dump_folder,
            game_path.replace("MatchDto", "MatchTimelineDto"),
        ),
        encoding="utf-8",
    ) as file:
        timeline_dto = json.load(file)

    with open(
        os.path.join(examples_folder, game_version + ".json"),
        "w+",
        encoding="utf-8",
    ) as file:
        json.dump({"match": match_dto, "timeline": timeline_dto}, file)
