import riotwatcher
import lol_dto
from riotwatcher._apis.league_of_legends import MatchApiV4
from riotwatcher_dto.match_dto_to_game import match_dto_to_game


class MatchApiDtoV4(MatchApiV4):
    def game_dto_by_id(self, region: str, match_id: int) -> lol_dto.LolGame:
        riot_match_dto = self.by_id(region, match_id)
        return match_dto_to_game(riot_match_dto)

    def timeline_dto_by_id(self, region: str, match_id: int) -> lol_dto.LolGame:
        pass

    def game_and_timeline_by_id(self, region: str, match_id: int) -> lol_dto.LolGame:
        pass


class LolWatcherDto(riotwatcher.LolWatcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._match = MatchApiDtoV4(self._base_api)
