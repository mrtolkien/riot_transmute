import lol_dto.classes.game as game_dto

import riot_transmute.v4
import riot_transmute.v5


def match_to_game(match_dto: dict, match_v5: bool = False) -> game_dto.LolGame:
    """
    Returns a LolGame from a MatchDto

    Currently works for both MatchV3 and MatchV4 from season 9 and later

    Args:
        match_dto: A MatchDto from Riot’s API
        match_v5: tag for match_v5 games, which have a different data structure

    Returns:
        The LolGame representation of the game
    """
    if match_v5:
        return riot_transmute.v5.match_to_game(match_dto)
    else:
        return riot_transmute.v4.match_to_game(match_dto)
