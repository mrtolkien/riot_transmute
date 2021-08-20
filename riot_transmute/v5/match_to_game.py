from datetime import datetime, timezone

import lol_dto.classes.game as dto


def match_to_game(match_dto: dict) -> dto.LolGame:
    """
    Returns a LolGame from a MatchDto from match-v5 endpoints

    Args:
        match_dto: A MatchDto from Riot's API,

    Returns:
        The LolGame representation of the game
    """
    log_prefix = (
        f"gameId {match_dto['gameId']}|" f"platformId {match_dto['platformId']}:\t"
    )
    info_log = set()

    # Creating some data fields in a friendlier format

    # ms timestamp -> ISO format
    date_time = datetime.utcfromtimestamp(match_dto["gameCreation"] / 1000).replace(
        tzinfo=timezone.utc
    )
    iso_creation_date = date_time.isoformat(timespec="seconds")

    # v5 has game start as well
    date_time = datetime.utcfromtimestamp(
        match_dto["gameStartTimestamp"] / 1000
    ).replace(tzinfo=timezone.utc)
    iso_start_date = date_time.isoformat(timespec="seconds")

    # only 2 values for the patch key (gameVersion is also saved)
    patch = ".".join(match_dto["gameVersion"].split(".")[:2])

    # Saving winner as BLUE or RED
    winner = (
        "BLUE"
        if (match_dto["teams"][0]["teamId"] == 100)
        == (match_dto["teams"][0]["win"] == "Win")
        else "RED"
    )

    # Creating our object's structure
    game = dto.LolGame(
        # Duration is in ms and not seconds in match v5
        duration=int(match_dto["gameDuration"] / 1000),
        creation=iso_creation_date,
        start=iso_start_date,
        patch=patch,
        gameVersion=match_dto["gameVersion"],
        winner=winner,
        lobbyName=match_dto["gameName"],
        type=match_dto["gameType"],
        queue_id=match_dto["queueId"],
    )

    return game
