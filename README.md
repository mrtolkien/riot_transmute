# Riot Transmute

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit enabled][pre-commit badge]][pre-commit project]
[![codecov](https://codecov.io/gh/mrtolkien/riot_transmute/branch/master/graph/badge.svg?token=R9DU7KJSPT)](https://codecov.io/gh/mrtolkien/riot_transmute)
[![Python Tests](https://github.com/mrtolkien/riot_transmute/actions/workflows/pr_tests_python.yml/badge.svg)](https://github.com/mrtolkien/riot_transmute/actions/workflows/pr_tests_python.yml)

[pre-commit badge]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
[pre-commit project]: https://pre-commit.com/

A simple wrapper to cast Riot API data to the [community-defined LoL DTO format](https://github.com/mrtolkien/lol_dto).

I recommend using [riotwatcher](https://pypi.org/project/riotwatcher/) or [pantheon](https://pypi.org/project/pantheon/)
 to acquire objects from the Riot API.

## Installation

`pip install riot_transmute`

## Usage

```python
import riot_transmute

game_from_match = riot_transmute.match_to_game(match_dto)
game_from_timeline = riot_transmute.match_timeline_to_game(match_timeline_dto, game_id, platform_id)
```

## Adding names to objects

### Install lol_dto extras

`pip install riot_transmute lol_dto[names]`

## Names usage

`game_with_names = riot_transmute.match_to_game(match)`
