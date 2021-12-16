import lol_dto


def merge_games_from_riot_match_and_timeline(
    game_from_match: lol_dto.classes.game.LolGame,
    game_from_timeline: lol_dto.classes.game.LolGame,
):
    """
    Merges a LolGame from match_to_game with a LolGame from match_timeline_to_game
    """
    game_from_match.kills = game_from_timeline.kills
    game_from_match.pauses = game_from_timeline.pauses

    # Timeline has GAME_END with the proper timestamp, the game_from_match only gets full time (with pauses)
    if game_from_timeline.duration:
        game_from_match.duration = game_from_timeline.duration

    for side in "BLUE", "RED":
        match_team = getattr(game_from_match.teams, side)
        timeline_team = getattr(game_from_timeline.teams, side)

        match_team: lol_dto.classes.game.LolGameTeam
        timeline_team: lol_dto.classes.game.LolGameTeam

        match_team.buildingsKills = timeline_team.buildingsKills
        match_team.epicMonstersKills = timeline_team.epicMonstersKills

        for match_player in match_team.players:
            timeline_player = next(
                p for p in timeline_team.players if p.id == match_player.id
            )

            # Match v5 gives us the puuid in the timeline
            if (
                hasattr(match_player.sources, "riot")
                and match_player.sources.riotLolApi.puuid
            ):
                assert (
                    match_player.sources.riotLolApi.puuid
                    == timeline_player.sources.riotLolApi.puuid
                )

            match_player.itemsEvents = timeline_player.itemsEvents
            match_player.skillsLevelUpEvents = timeline_player.skillsLevelUpEvents
            match_player.levelUpEvents = timeline_player.levelUpEvents
            match_player.snapshots = timeline_player.snapshots
            match_player.wardsEvents = timeline_player.wardsEvents
            match_player.specialKills = timeline_player.specialKills

    return game_from_match
