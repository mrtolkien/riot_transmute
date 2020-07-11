import lol_dto.classes.game as game_dto
import lol_id_tools as lit

from riot_transmute.logger import riot_transmute_logger
from riot_transmute.match_to_game import RiotGameIdentifier

monster_type_dict = {"RIFTHERALD": "RIFT_HERALD", "DRAGON": "DRAGON", "BARON_NASHOR": "BARON"}

monster_subtype_dict = {
    "FIRE_DRAGON": "INFERNAL",
    "AIR_DRAGON": "CLOUD",
    "EARTH_DRAGON": "MOUNTAIN",
    "WATER_DRAGON": "OCEAN",
    "ELDER_DRAGON": "ELDER",
}

building_dict = {
    (981, 10441): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="TOP", towerLocation="OUTER", side="BLUE"),
    (1512, 6699): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="TOP", towerLocation="INNER", side="BLUE"),
    (1169, 4287): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="TOP", towerLocation="INHIBITOR", side="BLUE"),
    (5846, 6396): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="MID", towerLocation="OUTER", side="BLUE"),
    (5048, 4812): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="MID", towerLocation="INNER", side="BLUE"),
    (3651, 3696): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="MID", towerLocation="INHIBITOR", side="BLUE"),
    (10504, 1029): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="BOT", towerLocation="OUTER", side="BLUE"),
    (6919, 1483): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="BOT", towerLocation="INNER", side="BLUE"),
    (4281, 1253): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="BOT", towerLocation="INHIBITOR", side="BLUE"),
    (1748, 2270): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="TOP", towerLocation="NEXUS", side="BLUE"),
    (2177, 1807): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="BOT", towerLocation="NEXUS", side="BLUE"),
    (1171, 3571): game_dto.LolGameTeamBuildingKill(type="INHIBITOR", lane="TOP", side="BLUE"),
    (3203, 3208): game_dto.LolGameTeamBuildingKill(type="INHIBITOR", lane="MID", side="BLUE"),
    (3452, 1236): game_dto.LolGameTeamBuildingKill(type="INHIBITOR", lane="BOT", side="BLUE"),
    (4318, 13875): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="TOP", towerLocation="OUTER", side="RED"),
    (7943, 13411): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="TOP", towerLocation="INNER", side="RED"),
    (10481, 13650): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="TOP", towerLocation="INHIBITOR", side="RED"),
    (8955, 8510): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="MID", towerLocation="OUTER", side="RED"),
    (9767, 10113): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="MID", towerLocation="INNER", side="RED"),
    (11134, 11207): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="MID", towerLocation="INHIBITOR", side="RED"),
    (13866, 4505): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="BOT", towerLocation="OUTER", side="RED"),
    (13327, 8226): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="BOT", towerLocation="INNER", side="RED"),
    (13624, 10572): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="BOT", towerLocation="INHIBITOR", side="RED"),
    (12611, 13084): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="TOP", towerLocation="NEXUS", side="RED"),
    (13052, 12612): game_dto.LolGameTeamBuildingKill(type="TOWER", lane="BOT", towerLocation="NEXUS", side="RED"),
    (11261, 13676): game_dto.LolGameTeamBuildingKill(type="INHIBITOR", lane="TOP", side="RED"),
    (11598, 11667): game_dto.LolGameTeamBuildingKill(type="INHIBITOR", lane="MID", side="RED"),
    (13604, 11316): game_dto.LolGameTeamBuildingKill(type="INHIBITOR", lane="BOT", side="RED"),
}


def get_player(game: game_dto.LolGame, participant_id: int) -> game_dto.LolGamePlayer:
    """Gets a player object from its participantId.
    """
    team_side = "BLUE" if participant_id < 6 else "RED"
    return next(p for p in game["teams"][team_side]["players"] if p["id"] == participant_id)


def match_timeline_to_game(
    match_timeline_dto: dict, game_id: int, platform_id: str, add_names: bool = False,
) -> game_dto.LolGame:
    """Returns a LolGame from a MatchTimelineDto.

    Args:
        match_timeline_dto: A MatchTimelineDto from Riot’s API.
        game_id: The gameId of the game, required as it is not present in the MatchTimelineDto.
        platform_id: The platformId of the game, required as it is not present in the MatchTimelineDto.
        add_names: whether or not to add names for human readability in the DTO. False by default.

    Returns:
        The LolGame representation of the game.
    """

    riot_source = {"riotLolApi": RiotGameIdentifier(gameId=game_id, platformId=platform_id)}

    # Creating the game_dto skeleton
    game = game_dto.LolGame(
        sources=riot_source,
        teams={
            "BLUE": game_dto.LolGameTeam(
                players=[
                    game_dto.LolGamePlayer(id=i, snapshots=[], itemsEvents=[], wardsEvents=[], skillsLevelUpEvents=[])
                    for i in range(1, 6)
                ],
                monstersKills=[],
                buildingsKills=[],
            ),
            "RED": game_dto.LolGameTeam(
                players=[
                    game_dto.LolGamePlayer(id=i, snapshots=[], itemsEvents=[], wardsEvents=[], skillsLevelUpEvents=[])
                    for i in range(6, 11)
                ],
                monstersKills=[],
                buildingsKills=[],
            ),
        },
        kills=[],
    )

    for frame in match_timeline_dto["frames"]:
        # We start by adding player information at the given snapshot timestamps
        for participant_frame in frame["participantFrames"].values():
            team_side = "BLUE" if participant_frame["participantId"] < 6 else "RED"

            # Finding the player with the same id in our game object
            player = next(
                p for p in game["teams"][team_side]["players"] if p["id"] == participant_frame["participantId"]
            )

            try:
                position = game_dto.Position(x=participant_frame["position"]["x"], y=participant_frame["position"]["y"])
            except KeyError:
                position = None

            snapshot = game_dto.LolGamePlayerSnapshot(
                timestamp=frame["timestamp"] / 1000,
                currentGold=participant_frame["currentGold"],
                totalGold=participant_frame["totalGold"],
                xp=participant_frame["xp"],
                level=participant_frame["level"],
                cs=participant_frame["minionsKilled"] + participant_frame["jungleMinionsKilled"],
                monstersKilled=participant_frame["jungleMinionsKilled"],
                position=position,
                # Next fields gotten with .get() so they are None if they haven’t been created by roleml
                totalGoldDiff=participant_frame.get("totalGoldDiff"),
                xpDiff=participant_frame.get("xpDiff"),
                csDiff=participant_frame.get("minionsKilledDiff"),
                monstersKilledDiff=participant_frame.get("jungleMinionsKilledDiff"),
            )

            player["snapshots"].append(snapshot)

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

                team = game["teams"]["BLUE" if event["killerId"] < 6 else "RED"]

                monster_type = monster_type_dict[event["monsterType"]]

                event_dto = game_dto.LolGameTeamMonsterKill(
                    timestamp=timestamp, type=monster_type, killerId=event["killerId"]
                )

                if monster_type == "DRAGON":
                    try:
                        event_dto["subType"] = monster_subtype_dict[event["monsterSubType"]]
                    # If we don’t know how to translate the monster subtype, we simply leave it as-is
                    except KeyError:
                        event_dto["subType"] = event["monsterSubType"]

                team["monstersKills"].append(event_dto)

            # Buildings kills
            elif event["type"] == "BUILDING_KILL":
                # The teamId here refers to the SIDE of the tower that was killed, so the opponents killed it
                team = game["teams"]["RED" if event["teamId"] == 100 else "BLUE"]

                # Get the prebuilt "building" event DTO
                event_dto = building_dict[event["position"]["x"], event["position"]["y"]]

                # Fill its timestamp
                event_dto["timestamp"] = timestamp

                if event.get("killerId"):
                    event_dto["killerId"] = event.get("killerId")

                team["buildingsKills"].append(event_dto)

            # Champions kills
            elif event["type"] == "CHAMPION_KILL":
                position = game_dto.Position(x=event["position"]["x"], y=event["position"]["y"])

                game["kills"].append(
                    game_dto.LolGameKill(
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

                player["skillsLevelUpEvents"].append(
                    game_dto.LolGamePlayerSkillLevelUpEvent(
                        timestamp=timestamp, slot=event["skillSlot"], type=event["levelUpType"]
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
                    item_event = game_dto.LolGamePlayerItemEvent(
                        timestamp=timestamp, type=event_type, id=event["afterId"], undoId=event["beforeId"]
                    )
                else:
                    item_event = game_dto.LolGamePlayerItemEvent(
                        timestamp=timestamp, type=event_type, id=event["itemId"]
                    )

                if add_names:
                    item_event["name"] = lit.get_name(item_event["id"], object_type="item")

                player["itemsEvents"].append(item_event)

            # Wards placing and killing
            elif "WARD" in event["type"]:
                if event["type"] == "WARD_KILL":
                    if not event.get("killerId"):
                        riot_transmute_logger.debug(f"Ward kill event without killerId dropped:\n{event}")
                        continue
                    player = get_player(game, event["killerId"])
                    event_type = "KILLED"
                else:
                    try:
                        player = get_player(game, event["creatorId"])
                    except StopIteration:
                        # TODO Understand events with ward_type=UNDEFINED + creatorId=0, they are dropped atm
                        continue
                    event_type = "PLACED"

                player["wardsEvents"].append(
                    game_dto.LolGamePlayerWardEvent(timestamp=timestamp, type=event_type, wardType=event["wardType"])
                )

    return game
