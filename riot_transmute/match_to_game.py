from typing import TypedDict

import lol_dto.classes.game as game_dto
import lol_id_tools as lit
from datetime import datetime, timezone


class RiotGameIdentifier(TypedDict):
    gameId: int
    platformId: str


def match_to_game(match_dto: dict, add_names: bool = False) -> game_dto.LolGame:
    """Returns a LolGame from a MatchDto.

    Args:
        match_dto: A MatchDto from Riot’s API
        add_names: whether or not to add names for human readability in the DTO. False by default.

    Returns:
        The LolGame representation of the game.
    """
    riot_source = {
        "riotLolApi": RiotGameIdentifier(
            gameId=match_dto["gameId"], platformId=match_dto["platformId"]
        )
    }

    log_prefix = (
        f"gameId {match_dto['gameId']}|" f"platformId {match_dto['platformId']}:\t"
    )
    info_log = set()

    date_time = datetime.utcfromtimestamp(match_dto["gameCreation"] / 1000)
    date_time = date_time.replace(tzinfo=timezone.utc)
    iso_date = date_time.isoformat(timespec="seconds")

    patch = ".".join(match_dto["gameVersion"].split(".")[:2])
    winner = (
        "BLUE"
        if (match_dto["teams"][0]["teamId"] == 100)
        == (match_dto["teams"][0]["win"] == "Win")
        else "RED"
    )

    # TODO Change optional fields to .get() instead of [], do it in timeline too

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
            endOfGameStats=game_dto.LolGameTeamEndOfGameStats(
                riftHeraldKills=team.get("riftHeraldKills"),
                dragonKills=team.get("dragonKills"),
                baronKills=team.get("baronKills"),
                towerKills=team.get("towerKills"),
                inhibitorKills=team.get("inhibitorKills"),
                firstTower=team.get("firstTower"),
                firstInhibitor=team.get("firstInhibitor"),
                firstRiftHerald=team.get("firstRiftHerald"),
                firstDragon=team.get("firstDragon"),
                firstBaron=team.get("firstBaron"),
            )
        )

        team_dto["bans"] = [b["championId"] for b in team["bans"]]

        team_dto["players"] = []

        for participant in match_dto["participants"]:
            if participant["teamId"] != team["teamId"]:
                continue

            try:
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
                    unique_identifier = {}

            # Custom games don’t have identity info
            except KeyError:
                participant_identity = None
                unique_identifier = {}

            # TODO Make that backwards-compatible with pre-runes reforged games
            runes = [
                game_dto.LolGamePlayerRune(
                    id=participant["stats"].get(f"perk{i}"),
                    slot=i,
                    stats=[
                        participant["stats"].get(f"perk{i}Var{j}") for j in range(1, 4)
                    ],
                )
                for i in range(0, 6)
            ]

            # Adding stats perks
            runes.extend(
                [
                    game_dto.LolGamePlayerRune(
                        id=participant["stats"].get(f"statPerk{i}"), slot=i + 6,
                    )
                    for i in range(0, 3)
                ]
            )

            items = [
                game_dto.LolGamePlayerItem(
                    id=participant["stats"].get(f"item{i}"), slot=i
                )
                for i in range(0, 7)
            ]

            summoner_spells = [
                game_dto.LolGamePlayerSummonerSpell(
                    id=participant.get(f"spell{i}Id"), slot=i - 1
                )
                for i in range(1, 3)
            ]

            end_of_game_stats = game_dto.LolGamePlayerEndOfGameStats(
                items=items,
                firstBlood=participant["stats"].get("firstBloodKill"),
                firstBloodAssist=participant["stats"].get(
                    "firstBloodAssist"
                ),  # This field is wrong by default
                kills=participant["stats"].get("kills"),
                deaths=participant["stats"].get("deaths"),
                assists=participant["stats"].get("assists"),
                gold=participant["stats"].get("goldEarned"),
                # TODO Test with older games
                cs=int(participant["stats"].get("totalMinionsKilled") or 0)
                + int(participant["stats"].get("neutralMinionsKilled") or 0),
                level=participant["stats"].get("champLevel"),
                wardsPlaced=participant["stats"].get("wardsPlaced"),
                wardsKilled=participant["stats"].get("wardsKilled"),
                visionWardsBought=participant["stats"].get("visionWardsBoughtInGame"),
                visionScore=participant["stats"].get("visionScore"),
                killingSprees=participant["stats"].get("killingSprees"),
                largestKillingSpree=participant["stats"].get("largestKillingSpree"),
                doubleKills=participant["stats"].get("doubleKills"),
                tripleKills=participant["stats"].get("tripleKills"),
                quadraKills=participant["stats"].get("quadraKills"),
                pentaKills=participant["stats"].get("pentaKills"),
                monsterKills=participant["stats"].get("neutralMinionsKilled"),
                monsterKillsInAlliedJungle=participant["stats"].get(
                    "neutralMinionsKilledTeamJungle"
                ),
                monsterKillsInEnemyJungle=participant["stats"].get(
                    "neutralMinionsKilledEnemyJungle"
                ),
                totalDamageDealt=participant["stats"].get("totalDamageDealt"),
                physicalDamageDealt=participant["stats"].get("physicalDamageDealt"),
                magicDamageDealt=participant["stats"].get("magicDamageDealt"),
                totalDamageDealtToChampions=participant["stats"].get(
                    "totalDamageDealtToChampions"
                ),
                physicalDamageDealtToChampions=participant["stats"].get(
                    "physicalDamageDealtToChampions"
                ),
                magicDamageDealtToChampions=participant["stats"].get(
                    "magicDamageDealtToChampions"
                ),
                damageDealtToObjectives=participant["stats"].get(
                    "damageDealtToObjectives"
                ),
                damageDealtToTurrets=participant["stats"].get("damageDealtToTurrets"),
                totalDamageTaken=participant["stats"].get("totalDamageTaken"),
                physicalDamageTaken=participant["stats"].get("physicalDamageTaken"),
                magicDamageTaken=participant["stats"].get("magicalDamageTaken"),
                longestTimeSpentLiving=participant["stats"].get(
                    "longestTimeSpentLiving"
                ),
                largestCriticalStrike=participant["stats"].get("largestCriticalStrike"),
                goldSpent=participant["stats"].get("goldSpent"),
                totalHeal=participant["stats"].get("totalHeal"),
                totalUnitsHealed=participant["stats"].get("totalUnitsHealed"),
                damageSelfMitigated=participant["stats"].get("damageSelfMitigated"),
                totalTimeCCDealt=participant["stats"].get("totalTimeCrowdControlDealt"),
                timeCCingOthers=participant["stats"].get("timeCCingOthers"),
            )

            # The following fields have proved to be missing or buggy in multiple games

            if "firstTowerKill" in participant["stats"]:
                end_of_game_stats["firstTower"] = participant["stats"]["firstTowerKill"]
                end_of_game_stats["firstTowerAssist"] = participant["stats"].get(
                    "firstTowerAssist"
                )
            else:
                info_log.add(f"{log_prefix}Missing ['player']['firstTower']")

            if "firstInhibitorKill" in participant["stats"]:
                end_of_game_stats["firstInhibitor"] = participant["stats"][
                    "firstInhibitorKill"
                ]
                end_of_game_stats["firstInhibitorAssist"] = participant["stats"].get(
                    "firstInhibitorAssist"
                )
            else:
                info_log.add(f"{log_prefix}Missing ['player']['firstInhibitor']")

            player = game_dto.LolGamePlayer(
                id=participant["participantId"],
                championId=participant["championId"],
                uniqueIdentifiers=unique_identifier,
                primaryRuneTreeId=participant["stats"].get("perkPrimaryStyle"),
                secondaryRuneTreeId=participant["stats"].get("perkSubStyle"),
                runes=runes,
                summonerSpells=summoner_spells,
                endOfGameStats=end_of_game_stats,
            )

            if participant_identity:
                player["inGameName"] = participant_identity["summonerName"]
                player["profileIconId"] = participant_identity["profileIcon"]

            # roleml compatibility
            if "role" in participant:
                # TODO Remove that after roleml refactor
                if participant["role"] not in {"TOP", "JGL", "MID", "BOT", "SUP"}:
                    participant["role"] = {
                        "top": "TOP",
                        "jungle": "JGL",
                        "mid": "MID",
                        "bot": "BOT",
                        "supp": "SUP",
                    }[participant["role"]]
                player["role"] = participant["role"]

            # Then, we add convenience name fields for human readability if asked
            if add_names:
                player["championName"] = lit.get_name(
                    player["championId"], object_type="champion"
                )
                player["primaryRuneTreeName"] = lit.get_name(
                    player["primaryRuneTreeId"]
                )
                player["secondaryRuneTreeName"] = lit.get_name(
                    player["secondaryRuneTreeId"]
                )

                for item in player["endOfGameStats"]["items"]:
                    item["name"] = lit.get_name(item["id"], object_type="item")
                for rune in player["runes"]:
                    rune["name"] = lit.get_name(rune["id"], object_type="rune")
                for summoner_spell in player["summonerSpells"]:
                    summoner_spell["name"] = lit.get_name(
                        summoner_spell["id"], object_type="summoner_spell"
                    )

            team_dto["players"].append(player)

        # We want to make extra sure players are always ordered by Riot’s given id
        team_dto["players"] = sorted(team_dto["players"], key=lambda x: x["id"])

        if add_names:
            team_dto["bansNames"] = []
            for ban in team_dto["bans"]:
                team_dto["bansNames"].append(lit.get_name(ban, object_type="champion"))

        game["teams"][side] = team_dto

    return game
