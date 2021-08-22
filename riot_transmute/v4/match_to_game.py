from datetime import datetime, timezone

from lol_dto.classes import game as game_dto
from lol_dto.classes.game import LolGame
from lol_dto.classes.sources.riot_lol_api import RiotGameSource, RiotPlayerSource

from riot_transmute.common.constants import clean_roles
from riot_transmute.common.iso_date_from_ms import get_iso_date_from_ms_timestamp


def match_to_game(match_dto: dict) -> LolGame:
    """
    Returns a LolGame from a MatchDto

    Currently works for both MatchV3 and MatchV4 from season 9 and later

    Args:
        match_dto: A MatchDto from Riot’s API

    Returns:
        The LolGame representation of the game
    """
    log_prefix = (
        f"gameId {match_dto['gameId']}|" f"platformId {match_dto['platformId']}:\t"
    )
    info_log = set()

    iso_date = get_iso_date_from_ms_timestamp(match_dto["gameCreation"])

    patch = ".".join(match_dto["gameVersion"].split(".")[:2])
    winner = (
        "BLUE"
        if (match_dto["teams"][0]["teamId"] == 100)
        == (match_dto["teams"][0]["win"] == "Win")
        else "RED"
    )

    game = game_dto.LolGame(
        duration=match_dto["gameDuration"],
        start=iso_date,
        patch=patch,
        gameVersion=match_dto["gameVersion"],
        winner=winner,
    )

    setattr(
        game.sources,
        "riotLolApi",
        RiotGameSource(gameId=match_dto["gameId"], platformId=match_dto["platformId"]),
    )

    for team in match_dto["teams"]:
        side = "BLUE" if team["teamId"] == 100 else "RED"

        team_dto = game_dto.LolGameTeam(
            endOfGameStats=game_dto.LolGameTeamEndOfGameStats(
                riftHeraldKills=team.get("riftHeraldKills"),
                dragonKills=team.get("dragonKills"),
                baronKills=team.get("baronKills"),
                turretKills=team.get("towerKills"),
                inhibitorKills=team.get("inhibitorKills"),
                firstTurret=team.get("firstTower"),
                firstInhibitor=team.get("firstInhibitor"),
                firstRiftHerald=team.get("firstRiftHerald"),
                firstDragon=team.get("firstDragon"),
                firstBaron=team.get("firstBaron"),
            )
        )

        team_dto.bans = [b["championId"] for b in team["bans"]]

        for participant in match_dto["participants"]:
            if participant["teamId"] != team["teamId"]:
                continue

            try:
                participant_identity = next(
                    identity["player"]
                    for identity in match_dto["participantIdentities"]
                    if identity["participantId"] == participant["participantId"]
                )

            # Custom games also don’t have identity info
            except KeyError:
                participant_identity = None

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
                        id=participant["stats"].get(f"statPerk{i}"),
                        slot=i + 6,
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
                totalDamageShieldedOnTeammates=participant["stats"].get(
                    "totalDamageShieldedOnTeammates"
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
                end_of_game_stats.firstTurret = participant["stats"]["firstTowerKill"]
                end_of_game_stats.firstTurretAssist = participant["stats"].get(
                    "firstTowerAssist"
                )
            else:
                info_log.add(f"{log_prefix}Missing ['player']['firstTower']")

            if "firstInhibitorKill" in participant["stats"]:
                end_of_game_stats.firstInhibitor = participant["stats"][
                    "firstInhibitorKill"
                ]
                end_of_game_stats.firstInhibitorAssist = participant["stats"].get(
                    "firstInhibitorAssist"
                )
            else:
                info_log.add(f"{log_prefix}Missing ['player']['firstInhibitor']")

            player = game_dto.LolGamePlayer(
                id=participant["participantId"],
                championId=participant["championId"],
                primaryRuneTreeId=participant["stats"].get("perkPrimaryStyle"),
                secondaryRuneTreeId=participant["stats"].get("perkSubStyle"),
                runes=runes,
                summonerSpells=summoner_spells,
                endOfGameStats=end_of_game_stats,
            )

            # Esports matches do not have an accountId field, so we need to test here
            if participant_identity and "accountId" in participant_identity:
                setattr(
                    player.sources,
                    "riotLolApi",
                    RiotPlayerSource(
                        accountId=participant_identity["accountId"],
                        platformId=participant_identity["platformId"],
                    ),
                )

            if participant_identity:
                player.inGameName = participant_identity["summonerName"]
                player.profileIconId = participant_identity["profileIcon"]

            # roleml compatibility
            if "role" in participant:
                if participant["role"] not in {"TOP", "JGL", "MID", "BOT", "SUP"}:
                    participant["role"] = clean_roles[participant["role"]]

                player.role = participant["role"]

            team_dto.players.append(player)

        # We want to make extra sure players are always ordered by Riot’s given id
        team_dto.players = sorted(team_dto.players, key=lambda x: x.id)

        setattr(game.teams, side, team_dto)

    return game
