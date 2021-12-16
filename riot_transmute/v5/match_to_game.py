import lol_dto.classes.game as dto
from lol_dto.classes.sources.riot_lol_api import RiotGameSource, RiotPlayerSource

from riot_transmute.common.iso_date_from_ms import get_iso_date_from_ms_timestamp

role_trigrams = {
    "TOP": "TOP",
    "JUNGLE": "JGL",
    "MIDDLE": "MID",
    "BOTTOM": "BOT",
    "UTILITY": "SUP",
}

from dataclasses import dataclass


@dataclass
class RiotGameRankedSource(RiotGameSource):
    tournamentCode: str = None


def match_to_game(match_dto: dict) -> dto.LolGame:
    """
    Returns a LolGame from a MatchDto from match-v5 endpoints

    Args:
        match_dto: A MatchDto from Riot's API,

    Returns:
        The LolGame representation of the game
    """
    # Creating some data fields in a friendlier format

    # ms timestamp -> ISO format
    iso_creation_date = get_iso_date_from_ms_timestamp(match_dto["gameCreation"])

    # v5 has game start as well
    iso_start_date = get_iso_date_from_ms_timestamp(match_dto["gameStartTimestamp"])

    # only 2 values for the patch key (gameVersion is also saved)
    patch = ".".join(match_dto["gameVersion"].split(".")[:2])

    # Saving winner as BLUE or RED
    if not any(match_dto["teams"][i]["win"] in ["Win", True] for i in range(0, 2)):
        raise ValueError

    winner = (
        "BLUE"
        if (match_dto["teams"][0]["teamId"] == 100)
        == (
            (
                # I saw both between esports games and live games
                match_dto["teams"][0]["win"] == "Win"
                or match_dto["teams"][0]["win"] == True
            )
        )
        else "RED"
    )

    # Riot made changes to duration on 11.20
    # Prior to patch 11.20, this field returns the game length in milliseconds calculated from gameEndTimestamp - gameStartTimestamp.
    # Post patch 11.20, this field returns the max timePlayed of any participant in the game in seconds, which makes the behavior of this field consistent with that of match-v4.
    # The best way to handling the change in this field is to treat the value as milliseconds if the gameEndTimestamp field isn't in the response and
    # to treat the value as seconds if gameEndTimestamp is in the response.

    if not match_dto.get("gameEndTimestamp"):
        duration = int(match_dto["gameDuration"] / 1000)
    else:
        duration = int(match_dto["gameDuration"])

    # Creating our object's structure
    game = dto.LolGame(
        duration=duration,
        creation=iso_creation_date,
        start=iso_start_date,
        patch=patch,
        gameVersion=match_dto["gameVersion"],
        winner=winner,
        lobbyName=match_dto["gameName"],
        type=match_dto["gameType"],
        queue_id=match_dto["queueId"],
    )

    setattr(
        game.sources,
        "riotLolApi",
        RiotGameRankedSource(
            gameId=match_dto["gameId"],
            platformId=match_dto["platformId"],
            tournamentCode=match_dto.get("tournamentCode"),
        ),
    )

    for dto_team in match_dto["teams"]:
        if dto_team["teamId"] == 100:
            game_team = game.teams.BLUE
        elif dto_team["teamId"] == 200:
            game_team = game.teams.RED
        else:
            raise ValueError(f"{dto_team['teamId']=} value not supported")

        game_team.bans = [b["championId"] for b in dto_team["bans"]]

        game_team.endOfGameStats = dto.LolGameTeamEndOfGameStats(
            firstTurret=dto_team["objectives"]["tower"]["first"],
            turretKills=dto_team["objectives"]["tower"]["kills"],
            firstRiftHerald=dto_team["objectives"]["riftHerald"]["first"],
            riftHeraldKills=dto_team["objectives"]["riftHerald"]["kills"],
            firstDragon=dto_team["objectives"]["dragon"]["first"],
            dragonKills=dto_team["objectives"]["dragon"]["kills"],
            firstBaron=dto_team["objectives"]["baron"]["first"],
            baronKills=dto_team["objectives"]["baron"]["kills"],
            firstInhibitor=dto_team["objectives"]["inhibitor"]["first"],
            inhibitorKills=dto_team["objectives"]["inhibitor"]["kills"],
        )

    for dto_player in match_dto["participants"]:
        if dto_player["teamId"] == 100:
            game_team = game.teams.BLUE
        elif dto_player["teamId"] == 200:
            game_team = game.teams.RED
        else:
            raise ValueError(f"{dto_player['teamId']=} value not supported")

        game_player = dto.LolGamePlayer(
            id=dto_player["participantId"],
            inGameName=dto_player["summonerName"],
            role=role_trigrams.get(dto_player["individualPosition"]),
            championId=dto_player["championId"],
            primaryRuneTreeId=dto_player["perks"]["styles"][0]["style"],
            secondaryRuneTreeId=dto_player["perks"]["styles"][1]["style"],
        )

        setattr(
            game_player.sources,
            "riotLolApi",
            RiotPlayerSource(
                # We have to use get to also be compatible with esports games
                puuid=dto_player.get("puuid"),
                summonerId=dto_player.get("summonerId"),
            ),
        )

        # We extend the runes with the primary and secondary trees
        game_player.runes.extend(
            dto.LolGamePlayerRune(
                slot=len(game_player.runes),
                id=r["perk"],
                stats=[r["var1"], r["var2"], r["var3"]],
            )
            for style in dto_player["perks"]["styles"]
            for r in style["selections"]
        )

        # We then add stats perks
        game_player.runes.extend(
            [
                dto.LolGamePlayerRune(
                    slot=len(game_player.runes),
                    id=dto_player["perks"]["statPerks"]["offense"],
                ),
                dto.LolGamePlayerRune(
                    slot=len(game_player.runes) + 1,
                    id=dto_player["perks"]["statPerks"]["flex"],
                ),
                dto.LolGamePlayerRune(
                    slot=len(game_player.runes) + 2,
                    id=dto_player["perks"]["statPerks"]["defense"],
                ),
            ]
        )

        game_player.summonerSpells.extend(
            dto.LolGamePlayerSummonerSpell(
                # Bayes' GAMH data uses spell1Id instead of summoner1Id
                id=dto_player.get(f"summoner{spell_id}Id")
                or dto_player.get(f"spell{spell_id}Id"),
                slot=spell_id - 1,
                casts=dto_player[f"summoner{spell_id}Casts"],
            )
            for spell_id in (1, 2)
        )

        game_team.earlySurrendered = dto_player["teamEarlySurrendered"]

        items = [
            dto.LolGamePlayerItem(id=dto_player.get(f"item{i}"), slot=i)
            for i in range(0, 7)
        ]

        end_of_game_stats = dto.LolGamePlayerEndOfGameStats(
            items=items,
            firstBlood=dto_player["firstBloodKill"],
            firstBloodAssist=dto_player["firstBloodAssist"],
            kills=dto_player["kills"],
            deaths=dto_player["deaths"],
            assists=dto_player["assists"],
            gold=dto_player["goldEarned"],
            cs=int(dto_player["totalMinionsKilled"] or 0)
            + int(dto_player["neutralMinionsKilled"] or 0),
            level=dto_player["champLevel"],
            wardsPlaced=dto_player["wardsPlaced"],
            wardsKilled=dto_player["wardsKilled"],
            visionWardsBought=dto_player["visionWardsBoughtInGame"],
            visionScore=dto_player["visionScore"],
            killingSprees=dto_player["killingSprees"],
            largestKillingSpree=dto_player["largestKillingSpree"],
            doubleKills=dto_player["doubleKills"],
            tripleKills=dto_player["tripleKills"],
            quadraKills=dto_player["quadraKills"],
            pentaKills=dto_player["pentaKills"],
            monsterKills=dto_player["neutralMinionsKilled"],
            totalDamageDealt=dto_player["totalDamageDealt"],
            physicalDamageDealt=dto_player["physicalDamageDealt"],
            magicDamageDealt=dto_player["magicDamageDealt"],
            totalDamageDealtToChampions=dto_player["totalDamageDealtToChampions"],
            physicalDamageDealtToChampions=dto_player["physicalDamageDealtToChampions"],
            magicDamageDealtToChampions=dto_player["magicDamageDealtToChampions"],
            damageDealtToObjectives=dto_player["damageDealtToObjectives"],
            damageDealtToTurrets=dto_player["damageDealtToTurrets"],
            damageDealtToBuildings=dto_player["damageDealtToBuildings"],
            totalDamageTaken=dto_player["totalDamageTaken"],
            physicalDamageTaken=dto_player["physicalDamageTaken"],
            magicDamageTaken=dto_player["magicDamageTaken"],
            longestTimeSpentLiving=dto_player["longestTimeSpentLiving"],
            largestCriticalStrike=dto_player["largestCriticalStrike"],
            goldSpent=dto_player["goldSpent"],
            totalHeal=dto_player["totalHeal"],
            totalUnitsHealed=dto_player["totalUnitsHealed"],
            damageSelfMitigated=dto_player["damageSelfMitigated"],
            totalTimeCCDealt=dto_player["totalTimeCCDealt"],
            # New match-v5 fields
            xp=dto_player["champExperience"],
            bountyLevel=dto_player["bountyLevel"],
            baronKills=dto_player["baronKills"],
            dragonKills=dto_player["dragonKills"],
            inhibitorKills=dto_player["inhibitorKills"],
            inhibitorTakedowns=dto_player["inhibitorTakedowns"],
            championTransform=dto_player["championTransform"],
            consumablesPurchased=dto_player["consumablesPurchased"],
            detectorWardsPlaced=dto_player["detectorWardsPlaced"],
            itemsPurchased=dto_player["itemsPurchased"],
            nexusKills=dto_player["nexusKills"],
            nexusTakedowns=dto_player["nexusTakedowns"],
            objectivesStolen=dto_player["objectivesStolen"],
            objectivesStolenAssists=dto_player["objectivesStolenAssists"],
            sightWardsBoughtInGame=dto_player["sightWardsBoughtInGame"],
            totalDamageShieldedOnTeammates=dto_player["totalDamageShieldedOnTeammates"],
            totalHealsOnTeammates=dto_player["totalHealsOnTeammates"],
            totalTimeSpentDead=dto_player["totalTimeSpentDead"],
            turretTakedowns=dto_player["turretTakedowns"],
            turretKills=dto_player["turretKills"],
        )

        game_player.endOfGameStats = end_of_game_stats

        game_team.players.append(game_player)

    return game
