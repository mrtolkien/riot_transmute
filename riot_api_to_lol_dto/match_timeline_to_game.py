import lol_dto.classes as dto

monster_subtype_dict = {
    "FIRE_DRAGON": "INFERNAL",
    "AIR_DRAGON": "CLOUD",
    "EARTH_DRAGON": "MOUNTAIN",
    "WATER_DRAGON": "OCEAN",
    "ELDER_DRAGON": "ELDER",
}


building_dict = {
    (981, 10441): dto.LolGameTeamBuildingKill(type="TOWER", lane="TOP", towerLocation="OUTER", side="BLUE"),
    (1512, 6699): dto.LolGameTeamBuildingKill(type="TOWER", lane="TOP", towerLocation="INNER", side="BLUE"),
    (1169, 4287): dto.LolGameTeamBuildingKill(type="TOWER", lane="TOP", towerLocation="INHIBITOR", side="BLUE"),
    (5846, 6396): dto.LolGameTeamBuildingKill(type="TOWER", lane="MID", towerLocation="OUTER", side="BLUE"),
    (5048, 4812): dto.LolGameTeamBuildingKill(type="TOWER", lane="MID", towerLocation="INNER", side="BLUE"),
    (3651, 3696): dto.LolGameTeamBuildingKill(type="TOWER", lane="MID", towerLocation="INHIBITOR", side="BLUE"),
    (10504, 1029): dto.LolGameTeamBuildingKill(type="TOWER", lane="BOT", towerLocation="OUTER", side="BLUE"),
    (6919, 1483): dto.LolGameTeamBuildingKill(type="TOWER", lane="BOT", towerLocation="INNER", side="BLUE"),
    (4281, 1253): dto.LolGameTeamBuildingKill(type="TOWER", lane="BOT", towerLocation="INHIBITOR", side="BLUE"),
    (1748, 2270): dto.LolGameTeamBuildingKill(type="TOWER", lane="TOP", towerLocation="NEXUS", side="BLUE"),
    (2177, 1807): dto.LolGameTeamBuildingKill(type="TOWER", lane="BOT", towerLocation="NEXUS", side="BLUE"),
    (1171, 3571): dto.LolGameTeamBuildingKill(type="INHIBITOR", lane="TOP", towerLocation=None, side="BLUE"),
    (3203, 3208): dto.LolGameTeamBuildingKill(type="INHIBITOR", lane="MID", towerLocation=None, side="BLUE"),
    (3452, 1236): dto.LolGameTeamBuildingKill(type="INHIBITOR", lane="BOT", towerLocation=None, side="BLUE"),
    (4318, 13875): dto.LolGameTeamBuildingKill(type="TOWER", lane="TOP", towerLocation="OUTER", side="RED"),
    (7943, 13411): dto.LolGameTeamBuildingKill(type="TOWER", lane="TOP", towerLocation="INNER", side="RED"),
    (10481, 13650): dto.LolGameTeamBuildingKill(type="TOWER", lane="TOP", towerLocation="INHIBITOR", side="RED"),
    (8955, 8510): dto.LolGameTeamBuildingKill(type="TOWER", lane="MID", towerLocation="OUTER", side="RED"),
    (9767, 10113): dto.LolGameTeamBuildingKill(type="TOWER", lane="MID", towerLocation="INNER", side="RED"),
    (11134, 11207): dto.LolGameTeamBuildingKill(type="TOWER", lane="MID", towerLocation="INHIBITOR", side="RED"),
    (13866, 4505): dto.LolGameTeamBuildingKill(type="TOWER", lane="BOT", towerLocation="OUTER", side="RED"),
    (13327, 8226): dto.LolGameTeamBuildingKill(type="TOWER", lane="BOT", towerLocation="INNER", side="RED"),
    (13624, 10572): dto.LolGameTeamBuildingKill(type="TOWER", lane="BOT", towerLocation="INHIBITOR", side="RED"),
    (12611, 13084): dto.LolGameTeamBuildingKill(type="TOWER", lane="TOP", towerLocation="NEXUS", side="RED"),
    (13052, 12612): dto.LolGameTeamBuildingKill(type="TOWER", lane="BOT", towerLocation="NEXUS", side="RED"),
    (11261, 13676): dto.LolGameTeamBuildingKill(type="INHIBITOR", lane="TOP", towerLocation=None, side="RED"),
    (11598, 11667): dto.LolGameTeamBuildingKill(type="INHIBITOR", lane="MID", towerLocation=None, side="RED"),
    (13604, 11316): dto.LolGameTeamBuildingKill(type="INHIBITOR", lane="BOT", towerLocation=None, side="RED"),
}


def get_player(game: dto.LolGame, participant_id: int) -> dto.LolGamePlayer:
    """Gets a player object from its "participant id"
    """
    team_side = "BLUE" if participant_id < 6 else "RED"
    return next(p for p in game["teams"][team_side]["players"] if p["id"] == participant_id)


def get_team(game: dto.LolGame, participant_id: int) -> dto.LolGameTeam:
    team_side = "BLUE" if participant_id < 6 else "RED"
    return game["teams"][team_side]


def match_timeline_to_game(riot_timeline_dto: dict, game_id, platform_id, add_names: bool = False) -> dto.LolGame:
    """Returns a LolGame from a MatchTimelineDto
    """

    # TODO Use add_names and lol_id_tools to add names fields if asked

    riot_source = {"riotLolApi": {"gameId": game_id, "platformId": platform_id}}

    # Creating the game_dto skeleton
    game = dto.LolGame(
        sources=riot_source,
        teams={
            "BLUE": dto.LolGameTeam(
                players=[
                    dto.LolGamePlayer(id=i, snapshots=[], itemsEvents=[], wardsEvents=[], skillsEvents=[])
                    for i in range(1, 6)
                ],
                monstersKills=[],
                buildingsKills=[],
            ),
            "RED": dto.LolGameTeam(
                players=[
                    dto.LolGamePlayer(id=i, snapshots=[], itemsEvents=[], wardsEvents=[], skillsEvents=[])
                    for i in range(6, 11)
                ],
                monstersKills=[],
                buildingsKills=[],
            ),
        },
        kills=[],
    )

    for frame in riot_timeline_dto["frames"]:
        # We start by adding player information at the given snapshot timestamps
        for participant_frame in frame["participantFrames"].values():
            team_side = "BLUE" if participant_frame["participantId"] < 6 else "RED"

            # Finding the player with the same id in our game object
            player = next(
                p for p in game["teams"][team_side]["players"] if p["id"] == participant_frame["participantId"]
            )

            try:
                position = dto.Position(x=participant_frame["position"]["x"], y=participant_frame["position"]["y"])
            except KeyError:
                position = None

            snapshot = dto.LolGamePlayerSnapshot(
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
            timestamp = event["timestamp"] / 1000

            # Epic monsters kills
            if event["type"] == "ELITE_MONSTER_KILL":
                team = get_team(game, event["killerId"])

                event_dto = dto.LolGameTeamMonsterKill(
                    timestamp=timestamp, type=event["monsterType"], killerId=event["killerId"]
                )

                if event["type"] == "DRAGON":
                    try:
                        event_dto["subType"] = monster_subtype_dict[event["monsterSubType"]]
                    # If we don’t know how to translate the monster subtype, we simply leave it as-is
                    except KeyError:
                        event_dto["subType"] = event["monsterSubType"]

                team["monstersKills"].append(event_dto)

            # Buildings kills
            elif event["type"] == "BUILDING_KILL":
                team = get_team(game, event["killerId"])

                event_dto = building_dict[event["position"]["x"], event["position"]["y"]]
                event_dto["timestamp"] = timestamp

                team["buildingsKills"].append(event_dto)

            # Champions kills
            elif event["type"] == "CHAMPION_KILL":
                position = dto.Position(x=event["position"]["x"], y=event["position"]["y"])

                game["kills"].append(
                    dto.LolGameKill(
                        timestamp=timestamp,
                        position=position,
                        killerId=event["killerId"],
                        victimId=event["victimId"],
                        assistingParticipantIds=event["assistingParticipantIds"],
                    )
                )

            # Skill points use
            elif event["type"] == "SKILL_LEVEL_UP":
                player = get_player(game, event["participantId"])

                player["skillsEvents"].append(
                    dto.LolGamePlayerSkillEvent(
                        timestamp=timestamp, skillSlot=event["skillSlot"], type=event["levelUpType"]
                    )
                )

            # Item buying, selling, and undoing
            elif "ITEM" in event["type"]:
                player = get_player(game, event["participantId"])
                event_type = event["type"].lstrip("ITEM_")

                if event_type == "UNDO":
                    item_id = event["beforeId"]
                else:
                    item_id = event["itemId"]

                player["itemsEvents"].append(
                    dto.LolGamePlayerItemEvent(timestamp=timestamp, type=event_type, id=item_id)
                )

            # Wards placing and killing
            elif "WARD" in event["type"]:
                if event["type"] == "WARD_KILL":
                    player = get_player(game, event["killerId"])
                    event_type = "KILLED"
                else:
                    player = get_player(game, event["creatorId"])
                    event_type = "PLACED"

                player["wardsEvents"].append(
                    dto.LolGamePlayerWardEvent(timestamp=timestamp, type=event_type, wardType=event["wardType"])
                )

    return game
