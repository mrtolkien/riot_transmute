import lol_dto

monster_subtype_dict = {
    "FIRE_DRAGON": "INFERNAL",
    "AIR_DRAGON": "CLOUD",
    "EARTH_DRAGON": "MOUNTAIN",
    "WATER_DRAGON": "OCEAN",
    "ELDER_DRAGON": "ELDER",
}


building_position_dict = {
    (981, 10441): lol_dto.Building(buildingType="TOWER", lane="TOP", towerLocation="OUTER", side="blue"),
    (1512, 6699): lol_dto.Building(buildingType="TOWER", lane="TOP", towerLocation="INNER", side="blue"),
    (1169, 4287): lol_dto.Building(buildingType='TOWER', lane='TOP', towerLocation='INHIBITOR', side='blue'),

    (5846, 6396): lol_dto.Building(buildingType="TOWER", lane="MID", towerLocation="OUTER", side="blue"),
    (5048, 4812): lol_dto.Building(buildingType="TOWER", lane="MID", towerLocation="INNER", side="blue"),
    (3651, 3696): lol_dto.Building(buildingType='TOWER', lane='MID', towerLocation='INHIBITOR', side='blue'),

    (10504, 1029): lol_dto.Building(buildingType="TOWER", lane="BOT", towerLocation="OUTER", side="blue"),
    (6919, 1483): lol_dto.Building(buildingType="TOWER", lane="BOT", towerLocation="INNER", side="blue"),
    (4281, 1253): lol_dto.Building(buildingType='TOWER', lane='BOT', towerLocation='INHIBITOR', side='blue'),

    (1748, 2270): lol_dto.Building(buildingType='TOWER', lane='TOP', towerLocation='NEXUS', side='blue'),
    (2177, 1807): lol_dto.Building(buildingType='TOWER', lane='BOT', towerLocation='NEXUS', side='blue'),

    (1171, 3571): lol_dto.Building(buildingType="INHIBITOR", lane='TOP', towerLocation=None, side='blue'),
    (3203, 3208): lol_dto.Building(buildingType="INHIBITOR", lane='MID', towerLocation=None, side='blue'),
    (3452, 1236): lol_dto.Building(buildingType="INHIBITOR", lane='BOT', towerLocation=None, side='blue'),


    (4318, 13875): lol_dto.Building(buildingType="TOWER", lane="TOP", towerLocation="OUTER", side="red"),
    (7943, 13411): lol_dto.Building(buildingType="TOWER", lane="TOP", towerLocation="INNER", side="red"),
    (10481, 13650): lol_dto.Building(buildingType='TOWER', lane='TOP', towerLocation='INHIBITOR', side='red'),

    (8955, 8510): lol_dto.Building(buildingType="TOWER", lane="MID", towerLocation="OUTER", side="red"),
    (9767, 10113): lol_dto.Building(buildingType="TOWER", lane="MID", towerLocation="INNER", side="red"),
    (11134, 11207): lol_dto.Building(buildingType='TOWER', lane='MID', towerLocation='INHIBITOR', side='red'),

    (13866, 4505): lol_dto.Building(buildingType="TOWER", lane="BOT", towerLocation="OUTER", side="red"),
    (13327, 8226): lol_dto.Building(buildingType="TOWER", lane="BOT", towerLocation="INNER", side="red"),
    (13624, 10572): lol_dto.Building(buildingType='TOWER', lane='BOT', towerLocation='INHIBITOR', side='red'),

    (12611, 13084): lol_dto.Building(buildingType='TOWER', lane='TOP', towerLocation='NEXUS', side='red'),
    (13052, 12612): lol_dto.Building(buildingType='TOWER', lane='BOT', towerLocation='NEXUS', side='red'),

    (11261, 13676): lol_dto.Building(buildingType="INHIBITOR", lane='TOP', towerLocation=None, side='red'),
    (11598, 11667): lol_dto.Building(buildingType="INHIBITOR", lane='MID', towerLocation=None, side='red'),
    (13604, 11316): lol_dto.Building(buildingType="INHIBITOR", lane='BOT', towerLocation=None, side='red'),
}


def timeline_dto_to_game(riot_timeline_dto: dict, game_id, platform_id) -> lol_dto.LolGame:
    riot_source = {"riot": {"gameId": game_id, "platformId": platform_id}}

    # Creating the game_dto skeleton
    game = lol_dto.LolGame(
        sources=riot_source,
        teams={
            "blue": lol_dto.LolGameTeam(players=[lol_dto.LolGamePlayer(id=i, snapshots=[]) for i in range(1, 6)]),
            "red": lol_dto.LolGameTeam(players=[lol_dto.LolGamePlayer(id=i, snapshots=[]) for i in range(6, 11)]),
        },
        events=[],
    )

    for frame in riot_timeline_dto["frames"]:
        for participant_frame in frame["participantFrames"].values():
            team_side = "blue" if participant_frame["participantId"] < 6 else "red"

            player = next(
                p for p in game["teams"][team_side]["players"] if p["id"] == participant_frame["participantId"]
            )

            snapshot = lol_dto.LolGamePlayerSnapshot(
                currentGold=participant_frame["currentGold"],
                totalGold=participant_frame["totalGold"],
                xp=participant_frame["xp"],
                level=participant_frame["level"],
                cs=participant_frame["minionsKilled"] + participant_frame["jungleMinionsKilled"],
                monstersKilled=participant_frame["jungleMinionsKilled"],
            )

            player["snapshots"].append(snapshot)

        for event in frame["events"]:
            try:
                # We try to sanitize "playerId" as a field defining the player performing the event
                player_id = event.pop("participantId") if "participantId" in event else event.pop("killerId")
            except KeyError:
                # If neither participantId nor killerId is in the field, it is usually a kill made by minions
                player_id = None

            position = (
                lol_dto.Position(x=event["positions"]["x"], y=event["positions"]["y"]) if "position" in event else None
            )

            event_dto = lol_dto.LolGameEvent(
                timestamp=event.pop("timestamp") / 1000, type=event.pop("type"), playerId=player_id, position=position,
            )

            # First, we handle epic monster kills
            # TODO Should we change event type name? ELITE was never used in the history of the game
            if event_dto["type"] == "ELITE_MONSTER_KILL":
                event_dto["monster"] = lol_dto.Monster(monsterType=event["monsterType"])

                if event["monsterType"] == "DRAGON":
                    try:
                        event_dto["monster"]["monsterSubType"] = monster_subtype_dict[event["monsterSubType"]]
                    # If we don’t know how to translate the monster subtype, we simply leave it as-is
                    except KeyError:
                        event_dto["monster"]["monsterSubType"] = event["monsterSubType"]
            # Then, we handle tower kills with our buildings dictionary
            elif event_dto["type"] == "BUILDING_KILL":
                event_dto["building"] = building_position_dict[event['position']['x'], event['position']['y']]

    return game
