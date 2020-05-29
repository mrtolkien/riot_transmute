import lol_dto.classes as dto_classes

monster_subtype_dict = {
    "FIRE_DRAGON": "INFERNAL",
    "AIR_DRAGON": "CLOUD",
    "EARTH_DRAGON": "MOUNTAIN",
    "WATER_DRAGON": "OCEAN",
    "ELDER_DRAGON": "ELDER",
}


building_dict = {
    (981, 10441): dto_classes.Building(buildingType="TOWER", lane="TOP", towerLocation="OUTER", side="blue"),
    (1512, 6699): dto_classes.Building(buildingType="TOWER", lane="TOP", towerLocation="INNER", side="blue"),
    (1169, 4287): dto_classes.Building(buildingType="TOWER", lane="TOP", towerLocation="INHIBITOR", side="blue"),
    (5846, 6396): dto_classes.Building(buildingType="TOWER", lane="MID", towerLocation="OUTER", side="blue"),
    (5048, 4812): dto_classes.Building(buildingType="TOWER", lane="MID", towerLocation="INNER", side="blue"),
    (3651, 3696): dto_classes.Building(buildingType="TOWER", lane="MID", towerLocation="INHIBITOR", side="blue"),
    (10504, 1029): dto_classes.Building(buildingType="TOWER", lane="BOT", towerLocation="OUTER", side="blue"),
    (6919, 1483): dto_classes.Building(buildingType="TOWER", lane="BOT", towerLocation="INNER", side="blue"),
    (4281, 1253): dto_classes.Building(buildingType="TOWER", lane="BOT", towerLocation="INHIBITOR", side="blue"),
    (1748, 2270): dto_classes.Building(buildingType="TOWER", lane="TOP", towerLocation="NEXUS", side="blue"),
    (2177, 1807): dto_classes.Building(buildingType="TOWER", lane="BOT", towerLocation="NEXUS", side="blue"),
    (1171, 3571): dto_classes.Building(buildingType="INHIBITOR", lane="TOP", towerLocation=None, side="blue"),
    (3203, 3208): dto_classes.Building(buildingType="INHIBITOR", lane="MID", towerLocation=None, side="blue"),
    (3452, 1236): dto_classes.Building(buildingType="INHIBITOR", lane="BOT", towerLocation=None, side="blue"),
    (4318, 13875): dto_classes.Building(buildingType="TOWER", lane="TOP", towerLocation="OUTER", side="red"),
    (7943, 13411): dto_classes.Building(buildingType="TOWER", lane="TOP", towerLocation="INNER", side="red"),
    (10481, 13650): dto_classes.Building(buildingType="TOWER", lane="TOP", towerLocation="INHIBITOR", side="red"),
    (8955, 8510): dto_classes.Building(buildingType="TOWER", lane="MID", towerLocation="OUTER", side="red"),
    (9767, 10113): dto_classes.Building(buildingType="TOWER", lane="MID", towerLocation="INNER", side="red"),
    (11134, 11207): dto_classes.Building(buildingType="TOWER", lane="MID", towerLocation="INHIBITOR", side="red"),
    (13866, 4505): dto_classes.Building(buildingType="TOWER", lane="BOT", towerLocation="OUTER", side="red"),
    (13327, 8226): dto_classes.Building(buildingType="TOWER", lane="BOT", towerLocation="INNER", side="red"),
    (13624, 10572): dto_classes.Building(buildingType="TOWER", lane="BOT", towerLocation="INHIBITOR", side="red"),
    (12611, 13084): dto_classes.Building(buildingType="TOWER", lane="TOP", towerLocation="NEXUS", side="red"),
    (13052, 12612): dto_classes.Building(buildingType="TOWER", lane="BOT", towerLocation="NEXUS", side="red"),
    (11261, 13676): dto_classes.Building(buildingType="INHIBITOR", lane="TOP", towerLocation=None, side="red"),
    (11598, 11667): dto_classes.Building(buildingType="INHIBITOR", lane="MID", towerLocation=None, side="red"),
    (13604, 11316): dto_classes.Building(buildingType="INHIBITOR", lane="BOT", towerLocation=None, side="red"),
}


def match_timeline_to_game(riot_timeline_dto: dict, game_id, platform_id, add_names: bool = False) -> dto_classes.LolGame:
    """Returns a LolGame from a MatchTimelineDto
    """

    # TODO Use add_names and lol_id_tools to add names fields

    riot_source = {"riot": {"gameId": game_id, "platformId": platform_id}}

    # Creating the game_dto skeleton
    game = dto_classes.LolGame(
        sources=riot_source,
        teams={
            "blue": dto_classes.LolGameTeam(players=[dto_classes.LolGamePlayer(id=i, snapshots=[]) for i in range(1, 6)]),
            "red": dto_classes.LolGameTeam(players=[dto_classes.LolGamePlayer(id=i, snapshots=[]) for i in range(6, 11)]),
        },
        events=[],
    )

    for frame in riot_timeline_dto["frames"]:
        # We start by adding player information at the given snapshot timestamps
        for participant_frame in frame["participantFrames"].values():
            team_side = "blue" if participant_frame["participantId"] < 6 else "red"

            # Finding the player with the same id in our game object
            player = next(
                p for p in game["teams"][team_side]["players"] if p["id"] == participant_frame["participantId"]
            )

            try:
                position = dto_classes.Position(x=participant_frame["position"]["x"], y=participant_frame["position"]["y"])
            except KeyError:
                position = None

            snapshot = dto_classes.LolGamePlayerSnapshot(
                timestamp=frame["timestamp"] / 1000,
                currentGold=participant_frame["currentGold"],
                totalGold=participant_frame["totalGold"],
                xp=participant_frame["xp"],
                level=participant_frame["level"],
                cs=participant_frame["minionsKilled"] + participant_frame["jungleMinionsKilled"],
                monstersKilled=participant_frame["jungleMinionsKilled"],
                position=position,
            )

            player["snapshots"].append(snapshot)

        for event in frame["events"]:
            try:
                # We try to sanitize "playerId" as a field defining the player performing the event
                id_fields = ("participantId", "killerId", "creatorId")
                field = next(field for field in id_fields if field in event)
                player_id = event[field]
            except StopIteration:
                # If neither participantId nor killerId is in the field, it is usually a kill made by minions
                player_id = None

            event_dto = dto_classes.LolGameEvent(
                timestamp=event["timestamp"] / 1000, type=event["type"], playerId=player_id,
            )

            if "position" in event:
                event_dto["position"] = dto_classes.Position(x=event["position"]["x"], y=event["position"]["y"])

            # Then, we handle type-specific fields
            # Epic monster kills
            # TODO Should we change event type name? ELITE was never used in the history of the game
            if event["type"] == "ELITE_MONSTER_KILL":
                event_dto["monster"] = dto_classes.Monster(type=event["monsterType"])

                if event["type"] == "DRAGON":
                    try:
                        event_dto["monster"]["subType"] = monster_subtype_dict[event["monsterSubType"]]
                    # If we don’t know how to translate the monster subtype, we simply leave it as-is
                    except KeyError:
                        event_dto["monster"]["subType"] = event["monsterSubType"]
            # Building kills
            elif event["type"] == "BUILDING_KILL":
                # TODO Dropping teamId because it is redundant with the tower’s team side, ask
                event_dto["building"] = building_dict[event["position"]["x"], event["position"]["y"]]
            # Champion kills
            elif event["type"] == "CHAMPION_KILL":
                event_dto["victimId"] = event["victimId"]
                event_dto["assistingParticipantIds"] = event["assistingParticipantIds"]
            # Skill points use
            elif event["type"] == "SKILL_LEVEL_UP":
                event_dto["skillSlot"] = event["skillSlot"]
                event_dto["levelUpType"] = event["levelUpType"]
            # Item buying and use
            elif event["type"] in ["ITEM_PURCHASED", "ITEM_DESTROYED", "ITEM_SOLD"]:
                event_dto["itemId"] = event["itemId"]
            # Undoing items
            elif event["type"] == "ITEM_UNDO":
                event_dto["itemIdBeforeUndo"] = event["beforeId"]
                event_dto["itemIdAfterUndo"] = event["afterId"]
            elif event["type"] in ["WARD_PLACED", "WARD_KILL"]:
                event_dto["wardType"] = event["wardType"]
            else:
                # TODO REMOVE THIS
                print(event)

            game["events"].append(event_dto)

    # Making extra sure events are in chronological order
    # TODO Might be overkill, but you’re never too sure. Maybe should sort players snapshots too just in case.
    game["events"] = sorted(game["events"], key=lambda x: x["timestamp"])

    return game
