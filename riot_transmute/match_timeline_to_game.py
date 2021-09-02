import lol_dto
import riot_transmute.v4
import riot_transmute.v5
from riot_transmute.logger import riot_transmute_logger


def match_timeline_to_game(
    match_timeline_dto: dict,
    game_id: int,
    platform_id: str,
    match_v5: bool = False,
) -> lol_dto.classes.game.LolGame:
    """
    Returns a LolGame from a MatchTimelineDto

    Args:
        match_timeline_dto: A MatchTimelineDto from Riot’s API.
        game_id: The gameId of the game, required as it is not present in the MatchTimelineDto.
        platform_id: The platformId of the game, required as it is not present in the MatchTimelineDto.
        match_v5: flag for match_v5 timelines

    Returns:
        The LolGame representation of the game.
    """
    riot_transmute_logger.warning(
        DeprecationWarning(
            "This function will be removed in the near future, use the appropriate riot_transmute.v4 and "
            "riot_transmute.v5 functions instead"
        )
    )

    if not match_v5:
        return riot_transmute.v4.match_timeline_to_game(
            match_timeline_dto, game_id, platform_id
        )
    else:
        # TODO This needs metadata, so using the function creates issues... Maybe just drop it
        return riot_transmute.v5.match_timeline_to_game(match_timeline_dto)
