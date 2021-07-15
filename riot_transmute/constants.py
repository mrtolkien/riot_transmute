from lol_dto.classes import game as game_dto

clean_roles = {
    "top": "TOP",
    "jungle": "JGL",
    "mid": "MID",
    "bot": "BOT",
    "supp": "SUP",
}

monster_type_dict = {
    "RIFTHERALD": "RIFT_HERALD",
    "DRAGON": "DRAGON",
    "BARON_NASHOR": "BARON",
}

monster_subtype_dict = {
    "FIRE_DRAGON": "INFERNAL",
    "AIR_DRAGON": "CLOUD",
    "EARTH_DRAGON": "MOUNTAIN",
    "WATER_DRAGON": "OCEAN",
    "ELDER_DRAGON": "ELDER",
}

building_dict = {
    (981, 10441): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="TOP",
        turretLocation="OUTER",
        side="BLUE",
    ),
    (1512, 6699): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="TOP",
        turretLocation="INNER",
        side="BLUE",
    ),
    (1169, 4287): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="TOP",
        turretLocation="INHIBITOR",
        side="BLUE",
    ),
    (5846, 6396): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="MID",
        turretLocation="OUTER",
        side="BLUE",
    ),
    (5048, 4812): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="MID",
        turretLocation="INNER",
        side="BLUE",
    ),
    (3651, 3696): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="MID",
        turretLocation="INHIBITOR",
        side="BLUE",
    ),
    (10504, 1029): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="BOT",
        turretLocation="OUTER",
        side="BLUE",
    ),
    (6919, 1483): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="BOT",
        turretLocation="INNER",
        side="BLUE",
    ),
    (4281, 1253): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="BOT",
        turretLocation="INHIBITOR",
        side="BLUE",
    ),
    (1748, 2270): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="TOP",
        turretLocation="NEXUS",
        side="BLUE",
    ),
    (2177, 1807): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="BOT",
        turretLocation="NEXUS",
        side="BLUE",
    ),
    (1171, 3571): game_dto.LolGameTeamBuildingKill(
        type="INHIBITOR",
        lane="TOP",
        side="BLUE",
    ),
    (3203, 3208): game_dto.LolGameTeamBuildingKill(
        type="INHIBITOR",
        lane="MID",
        side="BLUE",
    ),
    (3452, 1236): game_dto.LolGameTeamBuildingKill(
        type="INHIBITOR",
        lane="BOT",
        side="BLUE",
    ),
    (4318, 13875): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="TOP",
        turretLocation="OUTER",
        side="RED",
    ),
    (7943, 13411): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="TOP",
        turretLocation="INNER",
        side="RED",
    ),
    (10481, 13650): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="TOP",
        turretLocation="INHIBITOR",
        side="RED",
    ),
    (8955, 8510): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="MID",
        turretLocation="OUTER",
        side="RED",
    ),
    (9767, 10113): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="MID",
        turretLocation="INNER",
        side="RED",
    ),
    (11134, 11207): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="MID",
        turretLocation="INHIBITOR",
        side="RED",
    ),
    (13866, 4505): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="BOT",
        turretLocation="OUTER",
        side="RED",
    ),
    (13327, 8226): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="BOT",
        turretLocation="INNER",
        side="RED",
    ),
    (13624, 10572): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="BOT",
        turretLocation="INHIBITOR",
        side="RED",
    ),
    (12611, 13084): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="TOP",
        turretLocation="NEXUS",
        side="RED",
    ),
    (13052, 12612): game_dto.LolGameTeamBuildingKill(
        type="TURRET",
        lane="BOT",
        turretLocation="NEXUS",
        side="RED",
    ),
    (11261, 13676): game_dto.LolGameTeamBuildingKill(
        type="INHIBITOR",
        lane="TOP",
        side="RED",
    ),
    (11598, 11667): game_dto.LolGameTeamBuildingKill(
        type="INHIBITOR",
        lane="MID",
        side="RED",
    ),
    (13604, 11316): game_dto.LolGameTeamBuildingKill(
        type="INHIBITOR",
        lane="BOT",
        side="RED",
    ),
}
