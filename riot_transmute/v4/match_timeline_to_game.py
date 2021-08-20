import warnings

import lol_dto

from riot_transmute.common.constants import (
    monster_type_dict,
    monster_subtype_dict,
    building_dict,
)
from riot_transmute.logger import riot_transmute_logger
from riot_transmute.common.get_player import get_player


def match_timeline_to_game(
    match_timeline_dto: dict,
    game_id: int,
    platform_id: str,
) -> lol_dto.classes.game.LolGame:

    # Creating the game_dto
    game = lol_dto.classes.game.LolGame()

    setattr(
        game.sources,
        "riotLolApi",
        lol_dto.classes.sources.riot_lol_api.RiotGameSource(
            gameId=game_id, platformId=platform_id
        ),
    )

    # We create empty Player objects with IDs from 1 to 10 to match the frames
    game.teams.BLUE.players = [
        lol_dto.classes.game.LolGamePlayer(id=i) for i in range(1, 6)
    ]
    game.teams.RED.players = [
        lol_dto.classes.game.LolGamePlayer(id=i) for i in range(6, 11)
    ]

    for frame in match_timeline_dto["frames"]:
        # We start by adding player information at the given snapshot timestamps
        for participant_frame in frame["participantFrames"].values():
            team = (
                game.teams.BLUE
                if participant_frame["participantId"] < 6
                else game.teams.RED
            )

            # Finding the player with the same id in our game object
            player = next(
                p for p in team.players if p.id == participant_frame["participantId"]
            )

            try:
                position = lol_dto.classes.game.Position(
                    x=participant_frame["position"]["x"],
                    y=participant_frame["position"]["y"],
                )
            except KeyError:
                position = None

            snapshot = lol_dto.classes.game.LolGamePlayerSnapshot(
                timestamp=frame["timestamp"] / 1000,
                currentGold=participant_frame["currentGold"],
                totalGold=participant_frame["totalGold"],
                xp=participant_frame["xp"],
                level=participant_frame["level"],
                cs=participant_frame["minionsKilled"]
                + participant_frame["jungleMinionsKilled"],
                monstersKilled=participant_frame["jungleMinionsKilled"],
                position=position,
            )

            player.snapshots.append(snapshot)

        for event in frame["events"]:
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

                event_dto = lol_dto.classes.game.LolGameTeamEpicMonsterKill(
                    timestamp=timestamp,
                    type=monster_type,
                    killerId=event["killerId"],
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

            # Buildings kills
            elif event["type"] == "BUILDING_KILL":
                # The teamId here refers to the SIDE of the tower that was killed, so the opponents killed it
                team = game.teams.RED if event["teamId"] == 100 else game.teams.BLUE

                # Get the prebuilt "building" event DTO
                event_dto = building_dict.get(
                    (event["position"]["x"], event["position"]["y"])
                )

                if not event_dto:
                    warnings.warn(
                        "Pre 4.20 games building kills do not get saved at the moment"
                    )
                    continue

                # Fill its timestamp
                event_dto.timestamp = timestamp

                if event.get("killerId"):
                    event_dto.killerId = event.get("killerId")

                team.buildingsKills.append(event_dto)

            # Champions kills
            elif event["type"] == "CHAMPION_KILL":
                position = lol_dto.classes.game.Position(
                    x=event["position"]["x"], y=event["position"]["y"]
                )

                game.kills.append(
                    lol_dto.classes.game.LolGameKill(
                        timestamp=timestamp,
                        position=position,
                        killerId=event["killerId"],
                        victimId=event["victimId"],
                        assistsIds=event["assistingParticipantIds"],
                    )
                )

            # Skill points use
            elif event["type"] == "SKILL_LEVEL_UP":
                player = get_player(game, event["participantId"])

                player.skillsLevelUpEvents.append(
                    lol_dto.classes.game.LolGamePlayerSkillLevelUpEvent(
                        timestamp=timestamp,
                        slot=event["skillSlot"],
                        type=event["levelUpType"],
                    )
                )

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
                    item_event = lol_dto.classes.game.LolGamePlayerItemEvent(
                        timestamp=timestamp,
                        type=event_type,
                        id=event["afterId"],
                        beforeUndoId=event["beforeId"],
                    )
                else:
                    item_event = lol_dto.classes.game.LolGamePlayerItemEvent(
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
                    lol_dto.classes.game.LolGamePlayerWardEvent(
                        timestamp=timestamp, type=event_type, wardType=event["wardType"]
                    )
                )

    return game
