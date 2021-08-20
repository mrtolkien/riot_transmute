import json
import os
import pytest

import riot_transmute
from riot_transmute.v5.match_to_game import role_trigrams

data_folder = os.path.join("tests", "data", "v5")


@pytest.mark.parametrize(
    "file_name", [f for f in os.listdir(data_folder) if "timeline" not in f]
)
def test_match_to_game_v5(file_name):
    with open(os.path.join(data_folder, file_name)) as file:
        match_dto = json.load(file)

        # For ranked games, the dto is in the info key
        if "info" in match_dto:
            match_dto = match_dto["info"]

    game = riot_transmute.match_to_game(match_dto, match_v5=True)

    assert game.winner in ["RED", "BLUE"]
    assert type(game.type) == str
    assert game.sources.riot.gameId
    assert game.sources.riot.platformId

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

        assert len(team.players) == 5

        for player in team.players:
            try:
                assert player.sources.riot.puuid
            except AssertionError:
                assert type(player.sources.riot.summonerId) == int

            assert player.id
            assert player.inGameName

            assert player.role in list(role_trigrams.values()) + [None]

            assert player.primaryRuneTreeId
            assert player.secondaryRuneTreeId

            assert player.runes

            assert player.summonerSpells
            for ss in player.summonerSpells:
                assert ss.casts is not None

            assert player.endOfGameStats.items

            assert player.endOfGameStats.objectivesStolen is not None
