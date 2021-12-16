import lol_dto.classes.game as game_dto

import riot_transmute.v4
import riot_transmute.v5
from riot_transmute.logger import riot_transmute_logger


def match_to_game(match_dto: dict, match_v5: bool = False) -> game_dto.LolGame:
    """
    Returns a LolGame from a MatchDto

    Args:
        match_dto: A MatchDto from Riot’s API
        match_v5: tag for match_v5 games, which have a different data structure

    Returns:
        The LolGame representation of the game
    """
    riot_transmute_logger.warning(
        DeprecationWarning(
            "This function will be removed in the near future, use the appropriate riot_transmute.v4 and "
            "riot_transmute.v5 functions instead"
        )
    )

    if match_v5:
        return riot_transmute.v5.match_to_game(match_dto)
    else:
        return riot_transmute.v4.match_to_game(match_dto)
