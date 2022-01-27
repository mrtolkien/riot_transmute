import warnings
from copy import deepcopy

import lol_dto.classes.game as dto
from lol_dto.classes.sources.riot_lol_api import RiotGameSource, RiotPlayerSource

from riot_transmute.common.get_player import get_player
from riot_transmute.common.constants import (
    monster_type_dict,
    monster_subtype_dict,
    building_dict,
)
from riot_transmute.common.iso_date_from_ms import get_iso_date_from_ms_timestamp
from riot_transmute.logger import riot_transmute_logger


def match_timeline_to_game(
    match_timeline_dto: dict, metadata: dict = None
) -> dto.LolGame:
    """
    Match-V5 timeline to LolGame

    Args:
        match_timeline_dto: the MatchTimelineDto from the API, 'info' field in the ranked API
        metadata: the metadata from the API, 'metadata' field in the ranked API

    """
    # Creating an empty game_dto
    game = dto.LolGame()

    if metadata:
        platform_id, game_id = metadata["matchId"].split("_")

        # Saving our unique identifier from the metadata if provided
        setattr(
            game.sources,
            "riotLolApi",
            RiotGameSource(gameId=int(game_id), platformId=platform_id),
        )

    else:
        # There is still a gameId for esports games, but no platform id for some reason
        setattr(
            game.sources,
            "riotLolApi",
            RiotGameSource(gameId=match_timeline_dto["gameId"]),
        )

    for participant in match_timeline_dto["participants"]:
        player = dto.LolGamePlayer(
            id=participant["participantId"],
        )

        setattr(
            player.sources,
            "riotLolApi",
            RiotPlayerSource(puuid=participant.get("puuid")),
        )

        if 1 <= player.id <= 5:
            game.teams.BLUE.players.append(player)
        elif 6 <= player.id <= 10:
            game.teams.RED.players.append(player)
        else:
            raise ValueError

    for frame in match_timeline_dto["frames"]:

        # We start by adding player information at the given snapshot timestamps
        for participant_frame in frame["participantFrames"].values():

            # Getting our player object
            player = get_player(game, participant_frame["participantId"])

            try:
                position = dto.Position(
                    x=participant_frame["position"]["x"],
                    y=participant_frame["position"]["y"],
                )
            except KeyError:
                position = None

            snapshot = dto.LolGamePlayerSnapshot(
                timestamp=frame["timestamp"] / 1000,
                currentGold=participant_frame["currentGold"],
                totalGold=participant_frame["totalGold"],
                xp=participant_frame["xp"],
                level=participant_frame["level"],
                cs=participant_frame["minionsKilled"]
                + participant_frame["jungleMinionsKilled"],
                monstersKilled=participant_frame["jungleMinionsKilled"],
                position=position,
                timeEnemySpentControlled=participant_frame["timeEnemySpentControlled"],
                damageStats=dto.LolGamePlayerSnapshotDamageStats(
                    **participant_frame["damageStats"]
                ),
                championStats=dto.LolGamePlayerSnapshotChampionStats(
                    **participant_frame["championStats"]
                ),
            )

            player.snapshots.append(snapshot)

        for event in frame["events"]:
            # TODO Make a common events handler function to reduce code duplication with v4

            timestamp = event["timestamp"] / 1000

            # Epic monsters kills
            if event["type"] == "ELITE_MONSTER_KILL":
                if event["killerId"] < 1:
                    # This is Rift Herald killing itself, we just pass
                    riot_transmute_logger.debug(
                        f"Epic monster kill with killer id 0 found, likely Rift Herald killing itself."
                    )
                    continue

                team = game.teams.BLUE if event["killerId"] < 6 else game.teams.RED
                monster_type = monster_type_dict[event["monsterType"]]

                event_dto = dto.LolGameTeamEpicMonsterKill(
                    timestamp=timestamp,
                    type=monster_type,
                    killerId=event["killerId"],
                    assistsIds=event.get("assistingParticipantIds"),
                )

                if monster_type == "DRAGON":
                    try:
                        event_dto.subType = monster_subtype_dict[
                            event["monsterSubType"]
                        ]
                    # If we don’t know how to translate the monster subtype, we simply leave it as-is
                    except KeyError:
                        # get to be compatible with pre 6.9 games
                        event_dto.subType = event.get("monsterSubType")

                team.epicMonstersKills.append(event_dto)

            # Buildings kills and turret plates
            elif (
                event["type"] == "BUILDING_KILL"
                or event["type"] == "TURRET_PLATE_DESTROYED"
            ):
                # The teamId here refers to the SIDE of the tower that was killed, so the opponents killed it
                team = game.teams.RED if event["teamId"] == 100 else game.teams.BLUE

                # Get a copy of the prebuilt "building" event DTO
                event_dto = deepcopy(
                    building_dict.get((event["position"]["x"], event["position"]["y"]))
                )

                # If it was a turret plate kill, we change the type from TURRET to TURRET_PLATE
                if event["type"] == "TURRET_PLATE_DESTROYED":
                    assert event_dto.type == "TURRET"
                    event_dto.type = "TURRET_PLATE"

                if not event_dto:
                    warnings.warn(
                        "Pre 4.20 games building kills do not get saved at the moment"
                    )
                    continue

                # Fill its information
                event_dto.timestamp = timestamp
                event_dto.killerId = event.get("killerId")
                event_dto.assistsIds = event.get("assistingParticipantIds")

                team.buildingsKills.append(event_dto)

            # Champions kills
            elif event["type"] == "CHAMPION_KILL":
                position = dto.Position(
                    x=event["position"]["x"], y=event["position"]["y"]
                )

                game.kills.append(
                    dto.LolGameKill(
                        timestamp=timestamp,
                        position=position,
                        killerId=event["killerId"],
                        victimId=event["victimId"],
                        # This is now *not there* if there are no assists
                        assistsIds=event.get("assistingParticipantIds") or [],
                        bounty=event["bounty"],
                        killStreakLength=event["killStreakLength"],
                        victimDamageDealt=[
                            dto.LolGameKillDamageInstance(**e)
                            for e in event.get("victimDamageDealt") or []
                        ],
                        victimDamageReceived=[
                            dto.LolGameKillDamageInstance(**e)
                            for e in event["victimDamageReceived"]
                        ],
                    )
                )

            # Skill points use
            elif event["type"] == "SKILL_LEVEL_UP":
                player = get_player(game, event["participantId"])

                player.skillsLevelUpEvents.append(
                    dto.LolGamePlayerSkillLevelUpEvent(
                        timestamp=timestamp,
                        slot=event["skillSlot"],
                        type=event["levelUpType"],
                    )
                )

            # Actual level ups
            elif event["type"] == "LEVEL_UP":
                player = get_player(game, event["participantId"])
                player.levelUpEvents.append(event["timestamp"] / 1000)
                continue

            # Item buying, selling, and undoing
            elif "ITEM" in event["type"]:
                if not event.get("participantId"):
                    riot_transmute_logger.debug(
                        f"Dropping item event because it does not have a participantId:\n{event}"
                    )
                    # Some weird ITEM_DESTROYED events without a participantId can appear in older games (tower items)
                    continue

                player = get_player(game, event["participantId"])
                event_type = event["type"].lstrip("ITEM_")

                if event_type == "UNDO":
                    item_event = dto.LolGamePlayerItemEvent(
                        timestamp=timestamp,
                        type=event_type,
                        id=event["afterId"],
                        beforeUndoId=event["beforeId"],
                    )
                else:
                    item_event = dto.LolGamePlayerItemEvent(
                        timestamp=timestamp, type=event_type, id=event["itemId"]
                    )

                player.itemsEvents.append(item_event)

            # Wards placing and killing
            elif "WARD" in event["type"]:
                if event["type"] == "WARD_KILL":
                    if not event.get("killerId"):
                        riot_transmute_logger.debug(
                            f"Ward kill event without killerId dropped:\n{event}"
                        )
                        continue
                    player = get_player(game, event["killerId"])
                    event_type = "KILLED"

                else:
                    try:
                        player = get_player(game, event["creatorId"])
                    except StopIteration:
                        # Events with ward_type=UNDEFINED and creatorId=0 are dropped at the moment
                        continue
                    event_type = "PLACED"

                player.wardsEvents.append(
                    dto.LolGamePlayerWardEvent(
                        timestamp=timestamp, type=event_type, wardType=event["wardType"]
                    )
                )

            # Happens once at the beginning of the game at least
            elif "PAUSE" in event["type"]:
                pause_event = dto.LolGamePause(
                    realTimestamp=get_iso_date_from_ms_timestamp(
                        event["realTimestamp"]
                    ),
                    type=event["type"],
                )
                game.pauses.append(pause_event)
                continue

            # Gives us the *proper* game end timestamp, *without counting pauses*
            elif event["type"] == "GAME_END":
                game.duration = event["timestamp"] / 1000
                continue

            elif event["type"] == "CHAMPION_SPECIAL_KILL":
                player = get_player(game, event["killerId"])
                position = dto.Position(
                    x=event["position"]["x"], y=event["position"]["y"]
                )

                assert player

                player.specialKills.append(
                    dto.LolGamePlayerSpecialKill(
                        timestamp=timestamp,
                        position=position,
                        type=event["type"],
                        multiKillLength=event.get("multiKillLength"),
                    )
                )

                continue

            elif event["type"] == "DRAGON_SOUL_GIVEN":
                if event["teamId"] == 100:
                    team = game.teams.BLUE
                elif event["teamId"] == 200:
                    team = game.teams.RED
                else:
                    raise ValueError

                team.epicMonstersKills.append(
                    dto.LolGameTeamEpicMonsterKill(
                        timestamp=timestamp,
                        type="DRAGON_SOUL",
                        subType=event["name"].upper(),
                    )
                )
                continue

            elif event["type"] == "CHAMPION_TRANSFORM":
                # TODO This happens when Kayn level ups, it is not handled at the moment
                continue

            # Events not handled, we raise
            else:
                raise ValueError(event)

    return game
