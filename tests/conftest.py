import os
import pytest
from riotwatcher import LolWatcher
import dotenv

dotenv.load_dotenv()


@pytest.fixture
def watcher():
    return LolWatcher(os.environ["RIOT_API_KEY"])
