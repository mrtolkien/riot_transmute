import json
import os

import pytest

import riot_transmute
from riot_transmute.v5.match_to_game import role_trigrams

data_folder = os.path.join("tests", "data", "v5")


# Testing a single game against specific values
def test_match_to_game_v5():
    with open(os.path.join(data_folder, f"match_v5_ranked.json")) as file:
        match_dto = json.load(file)["info"]

    game = riot_transmute.match_to_game(match_dto, match_v5=True)

    assert game.winner == "RED"
    assert game.patch == "11.16"
    assert game.type == "MATCHED_GAME"

    for team in game.teams:
        assert team.bans

        assert type(team.endOfGameStats.firstTurret) == bool
        assert type(team.endOfGameStats.firstBaron) == bool
        assert type(team.endOfGameStats.firstDragon) == bool
        assert type(team.endOfGameStats.firstRiftHerald) == bool
        assert type(team.endOfGameStats.firstInhibitor) == bool

        assert type(team.endOfGameStats.turretKills) == int
        assert type(team.endOfGameStats.baronKills) == int
        assert type(team.endOfGameStats.dragonKills) == int
        assert type(team.endOfGameStats.riftHeraldKills) == int
        assert type(team.endOfGameStats.inhibitorKills) == int

        assert team.players

        for player in team.players:
            assert player.id
            assert player.inGameName
            assert player.role in role_trigrams.values()

            assert player.primaryRuneTreeId
            assert player.secondaryRuneTreeId

            assert player.runes

            assert player.summonerSpells
            for ss in player.summonerSpells:
                assert ss.casts

            assert player.endOfGameStats.items

            assert player.endOfGameStats.objectivesStolen is not None
