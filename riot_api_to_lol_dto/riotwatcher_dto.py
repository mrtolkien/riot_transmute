import riotwatcher
import lol_dto
from riotwatcher._apis.league_of_legends import MatchApiV4
from riot_api_to_lol_dto.match_dto_to_game import match_dto_to_game
from riot_api_to_lol_dto.timeline_dto_to_game import timeline_dto_to_game


class MatchApiDtoV4(MatchApiV4):
    """A simple wrapper for the MatchV4 endpoints that we can cast to a LoL DTO.
    """
    def game_dto_by_id(self, region: str, match_id: int) -> lol_dto.LolGame:
        riot_match_dto = self.by_id(region, match_id)
        return match_dto_to_game(riot_match_dto)

    def timeline_dto_by_id(self, region: str, match_id: int) -> lol_dto.LolGame:
        riot_timeline_dto = self.timeline_by_match(region, match_id)
        return timeline_dto_to_game(riot_timeline_dto, game_id=match_id, platform_id=region)

    def game_and_timeline_by_id(self, region: str, match_id: int) -> lol_dto.LolGame:
        pass


class LolWatcherDto(riotwatcher.LolWatcher):
    """A RiotWatcher subclass adding LoL DTO support.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._match = MatchApiDtoV4(self._base_api)
