import lol_dto.classes as dto_classes
from datetime import datetime, timezone


def match_to_game(match_dto: dict, add_names: bool = False) -> dto_classes.LolGame:
    """Returns a LolGame from a MatchDto
    """
    # TODO Use add_names and lol_id_tools to add names fields

    riot_source = {"riotLolApi": {"gameId": match_dto["gameId"], "platformId": match_dto["platformId"]}}

    date_time = datetime.fromtimestamp(match_dto["gameCreation"] / 1000)
    date_time = date_time.replace(tzinfo=timezone.utc)
    iso_date = date_time.isoformat(timespec="seconds")

    patch = ".".join(match_dto["gameVersion"].split(".")[:2])
    winner = "BLUE" if (match_dto["teams"][0]["teamId"] == 100) == (match_dto["teams"][0]["win"] == "Win") else "RED"

    game_dto = dto_classes.LolGame(
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

        team_dto = dto_classes.LolGameTeam(
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

            # TODO See if we add all "identity" fields
            foreign_keys = {
                "riotLolApi": {
                    "accountId": participant_identity["accountId"],
                    "platformId": participant_identity["platformId"],
                }
            }

            runes = [
                dto_classes.LolGamePlayerRune(
                    id=participant["stats"][f"perk{i}"],
                    slot=i,
                    stats=[participant["stats"][f"perk{i}Var{j}"] for j in range(1, 4)],
                )
                for i in range(0, 6)
            ]

            items = [dto_classes.LolGamePlayerItem(id=participant["stats"][f"item{i}"], slot=i) for i in range(0, 7)]

            summoner_spells = [
                dto_classes.LolGamePlayerSummonerSpell(id=participant[f"spell{i}Id"], slot=i - 1) for i in range(1, 3)
            ]

            end_of_game_stats = dto_classes.LolGamePlayerStats(
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

            player = dto_classes.LolGamePlayer(
                id=participant["participantId"],
                inGameName=participant_identity["summonerName"],
                profileIconId=participant_identity["profileIcon"],
                championId=participant["championId"],
                foreignKeys=foreign_keys,
                primaryRuneTreeId=participant["stats"]["perkPrimaryStyle"],
                secondaryRuneTreeId=participant["stats"]["perkSubStyle"],
                runes=runes,
                summonerSpells=summoner_spells,
                endOfGameStats=end_of_game_stats,
            )

            team_dto["players"].append(player)

        # We want to make extra sure players are always ordered by id
        team_dto["players"] = sorted(team_dto["players"], key=lambda x: x["id"])

        game_dto["teams"][side] = team_dto

    return game_dto
