import riotwatcher
import lol_dto.utilities
import lol_dto.classes
from riotwatcher._apis.league_of_legends import MatchApiV4
from riot_api_to_lol_dto.match_to_game import match_to_game
from riot_api_to_lol_dto.match_timeline_to_game import match_timeline_to_game


class MatchApiDtoV4(MatchApiV4):
    """A simple wrapper for the MatchV4 endpoints that we can cast to a LoL DTO.

    More of a proof of concept class than anything, not meant to be use as-is.
    """
    def game_from_match(self, region: str, match_id: int) -> lol_dto.classes.LolGame:
        """Returns a LolGame with only MatchDto information"""
        riot_match_dto = self.by_id(region, match_id)
        return match_to_game(riot_match_dto)

    def game_from_timeline(self, region: str, match_id: int) -> lol_dto.classes.LolGame:
        """Returns a LolGame with only MatchTimelineDto information"""
        riot_timeline_dto = self.timeline_by_match(region, match_id)
        return match_timeline_to_game(riot_timeline_dto, game_id=match_id, platform_id=region)

    def full_game(self, region: str, match_id: int) -> lol_dto.classes.LolGame:
        """Returns a LolGame with all data available in the Riot API"""
        game_from_match = self.game_from_match(region, match_id)
        game_from_timeline = self.game_from_timeline(region, match_id)

        return lol_dto.utilities.merge_games(game_from_match, game_from_timeline)


class LolWatcherDto(riotwatcher.LolWatcher):
    """A RiotWatcher subclass adding LoL DTO support.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._match = MatchApiDtoV4(self._base_api)
