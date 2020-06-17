import lol_dto.classes.game as game_dto
import lol_id_tools as lit
from datetime import datetime, timezone


def match_to_game(match_dto: dict, add_names: bool = False) -> game_dto.LolGame:
    """Returns a LolGame from a MatchDto.

    Args:
        match_dto: A MatchDto from Riot’s API
        add_names: whether or not to add names for human readability in the DTO. False by default.

    Returns:
        The LolGame representation of the game.
    """

    riot_source = {"riotLolApi": {"gameId": match_dto["gameId"], "platformId": match_dto["platformId"]}}

    date_time = datetime.fromtimestamp(match_dto["gameCreation"] / 1000)
    date_time = date_time.replace(tzinfo=timezone.utc)
    iso_date = date_time.isoformat(timespec="seconds")

    patch = ".".join(match_dto["gameVersion"].split(".")[:2])
    winner = "BLUE" if (match_dto["teams"][0]["teamId"] == 100) == (match_dto["teams"][0]["win"] == "Win") else "RED"

    game = game_dto.LolGame(
        sources=riot_source,
        duration=match_dto["gameDuration"],
        start=iso_date,
        patch=patch,
        gameVersion=match_dto["gameVersion"],
        winner=winner,
        teams={},
    )

    for team in match_dto["teams"]:
        side = "BLUE" if team["teamId"] == 100 else "RED"

        # TODO Handle old games with elemental drakes before they were part of the API
        team_dto = game_dto.LolGameTeam(
            riftHeraldKills=team["riftHeraldKills"],
            dragonKills=team["dragonKills"],
            baronKills=team["baronKills"],
            towerKills=team["towerKills"],
            inhibitorKills=team["inhibitorKills"],
            firstTower=team["firstTower"],
            firstInhibitor=team["firstInhibitor"],
            firstRiftHerald=team["firstRiftHerald"],
            firstDragon=team["firstDragon"],
            firstBaron=team["firstBaron"],
        )

        team_dto["bans"] = [b["championId"] for b in team["bans"]]

        team_dto["players"] = []

        for participant in match_dto["participants"]:
            if participant["teamId"] != team["teamId"]:
                continue

            participant_identity = next(
                identity["player"]
                for identity in match_dto["participantIdentities"]
                if identity["participantId"] == participant["participantId"]
            )

            # Esports matches do not have an accountId field
            if "accountId" in participant_identity:
                unique_identifier = {
                    "riotLolApi": {
                        "accountId": participant_identity["accountId"],
                        "platformId": participant_identity["platformId"],
                    }
                }
            else:
                unique_identifier = None

            runes = [
                game_dto.LolGamePlayerRune(
                    id=participant["stats"][f"perk{i}"],
                    slot=i,
                    stats=[participant["stats"][f"perk{i}Var{j}"] for j in range(1, 4)],
                )
                for i in range(0, 6)
            ]

            items = [game_dto.LolGamePlayerItem(id=participant["stats"][f"item{i}"], slot=i) for i in range(0, 7)]

            summoner_spells = [
                game_dto.LolGamePlayerSummonerSpell(id=participant[f"spell{i}Id"], slot=i - 1) for i in range(1, 3)
            ]

            end_of_game_stats = game_dto.LolGamePlayerStats(
                items=items,
                firstBlood=participant["stats"]["firstBloodKill"],
                firstBloodAssist=participant["stats"]["firstBloodAssist"],  # This field is wrong by default
                firstTower=participant["stats"]["firstTowerKill"],
                firstTowerAssist=participant["stats"]["firstTowerAssist"],
                firstInhibitor=participant["stats"]["firstInhibitorKill"],
                firstInhibitorAssist=participant["stats"]["firstInhibitorAssist"],
                kills=participant["stats"]["kills"],
                deaths=participant["stats"]["deaths"],
                assists=participant["stats"]["assists"],
                gold=participant["stats"]["goldEarned"],
                cs=participant["stats"]["totalMinionsKilled"] + participant["stats"]["neutralMinionsKilled"],
                level=participant["stats"]["champLevel"],
                wardsPlaced=participant["stats"]["wardsPlaced"],
                wardsKilled=participant["stats"]["wardsKilled"],
                visionWardsBought=participant["stats"]["visionWardsBoughtInGame"],
                visionScore=participant["stats"]["visionScore"],
                killingSprees=participant["stats"]["killingSprees"],
                largestKillingSpree=participant["stats"]["largestKillingSpree"],
                doubleKills=participant["stats"]["doubleKills"],
                tripleKills=participant["stats"]["tripleKills"],
                quadraKills=participant["stats"]["quadraKills"],
                pentaKills=participant["stats"]["pentaKills"],
                monsterKills=participant["stats"]["neutralMinionsKilled"],
                monsterKillsInAlliedJungle=participant["stats"]["neutralMinionsKilledTeamJungle"],
                monsterKillsInEnemyJungle=participant["stats"]["neutralMinionsKilledEnemyJungle"],
                totalDamageDealt=participant["stats"]["totalDamageDealt"],
                physicalDamageDealt=participant["stats"]["physicalDamageDealt"],
                magicDamageDealt=participant["stats"]["magicDamageDealt"],
                totalDamageDealtToChampions=participant["stats"]["totalDamageDealtToChampions"],
                physicalDamageDealtToChampions=participant["stats"]["physicalDamageDealtToChampions"],
                magicDamageDealtToChampions=participant["stats"]["magicDamageDealtToChampions"],
                damageDealtToObjectives=participant["stats"]["damageDealtToObjectives"],
                damageDealtToTurrets=participant["stats"]["damageDealtToTurrets"],
                totalDamageTaken=participant["stats"]["totalDamageTaken"],
                physicalDamageTaken=participant["stats"]["physicalDamageTaken"],
                magicDamageTaken=participant["stats"]["magicalDamageTaken"],
                longestTimeSpentLiving=participant["stats"]["longestTimeSpentLiving"],
                largestCriticalStrike=participant["stats"]["largestCriticalStrike"],
                goldSpent=participant["stats"]["goldSpent"],
                totalHeal=participant["stats"]["totalHeal"],
                totalUnitsHealed=participant["stats"]["totalUnitsHealed"],
                damageSelfMitigated=participant["stats"]["damageSelfMitigated"],
                totalTimeCCDealt=participant["stats"]["totalTimeCrowdControlDealt"],
                timeCCingOthers=participant["stats"]["timeCCingOthers"],
            )

            player = game_dto.LolGamePlayer(
                id=participant["participantId"],
                inGameName=participant_identity["summonerName"],
                profileIconId=participant_identity["profileIcon"],
                championId=participant["championId"],
                uniqueIdentifiers=unique_identifier,
                primaryRuneTreeId=participant["stats"]["perkPrimaryStyle"],
                secondaryRuneTreeId=participant["stats"]["perkSubStyle"],
                runes=runes,
                summonerSpells=summoner_spells,
                endOfGameStats=end_of_game_stats,
            )

            # Then, we add convenience name fields for human readability if asked
            if add_names:
                player["championName"] = lit.get_name(player["championId"], object_type="champion")
                player["primaryRuneTreeName"] = lit.get_name(player["primaryRuneTreeId"])
                player["secondaryRuneTreeName"] = lit.get_name(player["secondaryRuneTreeId"])

                for item in player["endOfGameStats"]["items"]:
                    item["name"] = lit.get_name(item["id"], object_type="item")
                for rune in player["runes"]:
                    rune["name"] = lit.get_name(rune["id"], object_type="rune")
                for summoner_spell in player["summonerSpells"]:
                    summoner_spell["name"] = lit.get_name(summoner_spell["id"], object_type="summoner_spell")

            team_dto["players"].append(player)

        # We want to make extra sure players are always ordered by Riot’s given id
        team_dto["players"] = sorted(team_dto["players"], key=lambda x: x["id"])

        if add_names:
            team_dto["bansNames"] = []
            for ban in team_dto["bans"]:
                team_dto["bansNames"].append(lit.get_name(ban, object_type="champion"))

        game["teams"][side] = team_dto

    return game
