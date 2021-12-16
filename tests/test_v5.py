import json
import os
import pytest

import riot_transmute
from riot_transmute.v5.match_to_game import role_trigrams

data_folder = os.path.join("tests", "data", "v5")

# TODO Add tests with pre 11.20 games and post 11.20 to test for the duration format change


@pytest.mark.parametrize(
    "file_name", [f for f in os.listdir(data_folder) if "timeline" not in f]
)
def test_match_to_game_v5(file_name):
    with open(os.path.join(data_folder, file_name)) as file:
        match_dto = json.load(file)

        # For ranked games, the dto is in the info key and we drop the metadata
        if "info" in match_dto:
            match_dto = match_dto["info"]

    game = riot_transmute.v5.match_to_game(match_dto)

    assert game.winner in ["RED", "BLUE"]
    assert type(game.type) == str
    assert game.sources.riotLolApi.gameId
    assert game.sources.riotLolApi.platformId

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
                # This is ranked games
                assert player.sources.riotLolApi.puuid
                assert type(player.sources.riotLolApi.summonerId) == str
            except AssertionError:
                # If we get here this is an esport game, where the summonerId is clear
                assert type(player.sources.riotLolApi.summonerId) == int

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


@pytest.mark.parametrize(
    "file_name", [f for f in os.listdir(data_folder) if "timeline" in f]
)
def test_match_timeline_to_game_v5(file_name):
    with open(os.path.join(data_folder, file_name)) as file:
        timeline_dto = json.load(file)
        metadata = None

        # For ranked games, the dto is in the info key and we drop the metadata
        if "info" in timeline_dto:
            metadata = timeline_dto["metadata"]
            timeline_dto = timeline_dto["info"]

    timeline = riot_transmute.v5.match_timeline_to_game(timeline_dto, metadata)

    for kill in timeline.kills:
        assert kill.bounty
        assert kill.victimDamageReceived

        for damage_instance in kill.victimDamageReceived:
            assert damage_instance.type

    assert timeline.pauses
    for pause in timeline.pauses:
        assert pause.type in ["PAUSE_START", "PAUSE_END"]

    for side, team in (("BLUE", timeline.teams.BLUE), ("RED", timeline.teams.RED)):
        # Testing that each team got at least one plate
        try:
            assert len([e for e in team.buildingsKills if e.type == "TURRET_PLATE"])
        except AssertionError:
            # We check no towers were killed before 14 minutes to double-check
            assert not len(
                [
                    e
                    for e in team.buildingsKills
                    if e.type == "TURRET" and e.timestamp < 60 * 14
                ]
            )

        for monster_kill in team.epicMonstersKills:
            if "DRAGON" in monster_kill.type:
                assert monster_kill.subType in [
                    "CLOUD",
                    "INFERNAL",
                    "MOUNTAIN",
                    "OCEAN",
                    "ELDER",
                ]

        for player in team.players:
            assert player.snapshots
            assert player.levelUpEvents

            for snapshot in player.snapshots:
                assert snapshot.championStats.armor is not None
                assert snapshot.damageStats.trueDamageDone is not None

                assert snapshot.timeEnemySpentControlled is not None


@pytest.mark.parametrize(
    "file_name", [f for f in os.listdir(data_folder) if "timeline" not in f]
)
def test_merge_v5(file_name):
    with open(os.path.join(data_folder, file_name)) as file:
        match_dto = json.load(file)

        # For ranked games, the dto is in the info key and we drop the metadata
        if "info" in match_dto:
            match_dto = match_dto["info"]

    with open(os.path.join(data_folder, file_name)[:-5] + "_timeline.json") as file:
        timeline_dto = json.load(file)
        metadata = None

        # For ranked games, the dto is in the info key and we drop the metadata
        if "info" in timeline_dto:
            metadata = timeline_dto["metadata"]
            timeline_dto = timeline_dto["info"]

    game = riot_transmute.v5.match_to_game(match_dto)
    timeline = riot_transmute.v5.match_timeline_to_game(timeline_dto, metadata)

    merged_game = riot_transmute.merge_games_from_riot_match_and_timeline(
        game, timeline
    )

    assert merged_game

    assert merged_game.kills
    assert merged_game.pauses

    special_kills = False

    for team in merged_game.teams:
        for player in team.players:
            # This is from timeline
            assert player.snapshots
            assert player.levelUpEvents

            if player.specialKills:
                special_kills = True

            # This is from details
            assert player.runes

    assert special_kills
