import requests
from functools import lru_cache
from typing import List, Optional
from icetime.models import Team, Game, Season, GameResult, Shift, Player, TeamRoster

STATS_BASE_URL = "https://api.nhle.com/stats/rest/en"
WEB_BASE_URL = "https://api-web.nhle.com/v1"


class NotFoundError(Exception):
    pass


class StatsApi:
    """NHL Stats API client for fetching hockey data."""

    def __init__(
        self, stats_base_url: str = STATS_BASE_URL, web_base_url: str = WEB_BASE_URL
    ):
        self.session = requests.Session()
        self.__stats_base_url = stats_base_url
        self.__web_base_url = web_base_url

    @lru_cache(maxsize=1)
    def get_teams(self) -> List[Team]:
        """Fetch all NHL teams data (cached)."""
        url = f"{self.__stats_base_url}/team"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()

        # Sort the data array by id field
        if "data" in data and isinstance(data["data"], list):
            data["data"] = sorted(data["data"], key=lambda x: x.get("id", 0))

        # Convert to list of Team models
        if "data" in data and isinstance(data["data"], list):
            teams = [Team(**team) for team in data["data"]]
            return teams
        else:
            return []

    @lru_cache(maxsize=1)
    def get_games(self) -> List[Game]:
        """Fetch all NHL games data (cached)."""
        url = f"{self.__stats_base_url}/game"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()

        # Sort the data array by id field
        if "data" in data and isinstance(data["data"], list):
            data["data"] = sorted(data["data"], key=lambda x: x.get("id", 0))

        # Convert to list of Game models
        if "data" in data and isinstance(data["data"], list):
            games = [Game(**game) for game in data["data"]]
            return games
        else:
            return []

    @lru_cache(maxsize=1)
    def get_seasons(self) -> List[Season]:
        """Fetch all NHL seasons data (cached)."""
        url = f"{self.__stats_base_url}/season"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()

        # Sort the data array by id field
        if "data" in data and isinstance(data["data"], list):
            data["data"] = sorted(data["data"], key=lambda x: x.get("id", 0))

        # Convert to list of Season models
        if "data" in data and isinstance(data["data"], list):
            seasons = [Season(**season) for season in data["data"]]
            return seasons
        else:
            return []

    def get_games_by_season(self, season: int) -> List[Game]:
        """Fetch games filtered by season."""
        games = self.get_games()

        return [game for game in games if game.season == season]

    @lru_cache(maxsize=1)
    def get_play_by_play(self, game: Game) -> Optional[GameResult]:
        """Fetch game result data for a specific game (cached)."""
        game_id = game.id
        url = f"{self.__web_base_url}/gamecenter/{game_id}/play-by-play"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            return GameResult(**data)
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404:
                raise NotFoundError(f"Game result not found for game ID {game_id}")
            raise

    @lru_cache(maxsize=1)
    def get_shift_charts(self, game: Game) -> List[Shift]:
        """Fetch shift chart data for a specific game (cached)."""
        game_id = game.id
        url = f"{self.__stats_base_url}/shiftcharts"
        params = {"cayenneExp": f"gameId={game_id}"}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Convert to list of Shift models
            if "data" in data and isinstance(data["data"], list):
                shifts = []
                for shift_data in data["data"]:
                    # Add game_type from the Game argument
                    shift_data["game_type"] = game.game_type
                    shifts.append(Shift(**shift_data))
                return shifts
            else:
                return []
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404:
                raise NotFoundError(f"Shift chart data not found for game ID {game_id}")
            raise

    @lru_cache(maxsize=1024)
    def get_player(self, player_id: int) -> Optional[Player]:
        """Fetch player details for a specific player ID (cached)."""
        url = f"{self.__web_base_url}/player/{player_id}/landing"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            return Player(**data)
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404:
                raise NotFoundError(f"Player not found for player ID {player_id}")
            raise

    @lru_cache(maxsize=128)
    def get_roster_by_season(
        self, team_abbrev: str, season: int
    ) -> Optional[TeamRoster]:
        """Fetch team roster for a specific team and season (cached)."""
        url = f"{self.__web_base_url}/roster/{team_abbrev}/{season}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            # Transform the complex roster data to just player IDs
            roster_data = {
                "forwards": [player["id"] for player in data.get("forwards", [])],
                "defensemen": [player["id"] for player in data.get("defensemen", [])],
                "goalies": [player["id"] for player in data.get("goalies", [])],
            }

            return TeamRoster(**roster_data)
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404:
                raise NotFoundError(
                    f"Roster not found for team {team_abbrev} in season {season}"
                )
            raise
