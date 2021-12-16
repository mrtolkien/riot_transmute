import lol_dto


def get_player(
    game: lol_dto.classes.game.LolGame, participant_id: int
) -> lol_dto.classes.game.LolGamePlayer:
    """
    Gets a player object from its participantId
    """
    team = game.teams.BLUE if participant_id < 6 else game.teams.RED
    return next(p for p in team.players if p.id == participant_id)
