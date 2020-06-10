[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Riot transmute
A simple wrapper to cast Riot API data to the [community-defined LoL DTO format](https://github.com/mrtolkien/lol_dto).

I recommend using [riotwatcher](https://pypi.org/project/riotwatcher/) or [pantheon](https://pypi.org/project/pantheon/)
 to acquire objects from the Riot API.

# Installation
`pip install riot_transmute`

# Usage
```python
import riot_transmute

game_from_match = riot_transmute.match_to_game(match)
game_from_timeline = riot_transmute.match_timeline_to_game(match_timeline, game_id, platform_id)
```

# Adding names to objects
## Install extras
`pip install riot_transmute[names]`
## Usage
`game_witch_names = riot_transmute.match_to_game(match, add_names=True)`