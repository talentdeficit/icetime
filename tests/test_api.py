import pytest
import requests
import requests_mock
from icetime.api import StatsApi, NotFoundError
from icetime.models import Team, Game, Season, Shift, Player, TeamRoster


class TestStatsApi:
    def test_init_default_urls(self):
        api = StatsApi()
        assert api._StatsApi__stats_base_url == "https://api.nhle.com/stats/rest/en"
        assert api._StatsApi__web_base_url == "https://api-web.nhle.com/v1"

    def test_init_custom_urls(self):
        stats_url = "https://custom-stats.example.com"
        web_url = "https://custom-web.example.com"
        api = StatsApi(stats_base_url=stats_url, web_base_url=web_url)
        assert api._StatsApi__stats_base_url == stats_url
        assert api._StatsApi__web_base_url == web_url

    @pytest.mark.unit
    def test_get_teams_success(self, sample_team_data):
        with requests_mock.Mocker() as m:
            m.get("https://api.nhle.com/stats/rest/en/team", json=sample_team_data)

            api = StatsApi()
            teams = api.get_teams()

            assert len(teams) == 62
            assert isinstance(teams[0], Team)
            assert teams[0].id == 1
            assert teams[0].full_name == "New Jersey Devils"

    @pytest.mark.unit
    def test_get_teams_empty_response(self):
        with requests_mock.Mocker() as m:
            m.get("https://api.nhle.com/stats/rest/en/team", json={})

            api = StatsApi()
            teams = api.get_teams()

            assert teams == []

    @pytest.mark.unit
    def test_get_teams_http_error(self):
        with requests_mock.Mocker() as m:
            m.get("https://api.nhle.com/stats/rest/en/team", status_code=500)

            api = StatsApi()
            with pytest.raises(requests.exceptions.HTTPError):
                api.get_teams()

    @pytest.mark.unit
    def test_get_games_success(self, sample_game_data):
        with requests_mock.Mocker() as m:
            m.get("https://api.nhle.com/stats/rest/en/game", json=sample_game_data)

            api = StatsApi()
            games = api.get_games()

            assert len(games) == 2
            assert isinstance(games[0], Game)
            assert games[0].id == 1917020001
            assert games[0].season == 19171918

    @pytest.mark.unit
    def test_get_seasons_success(self, sample_season_data):
        with requests_mock.Mocker() as m:
            m.get("https://api.nhle.com/stats/rest/en/season", json=sample_season_data)

            api = StatsApi()
            seasons = api.get_seasons()

            assert len(seasons) == 107
            assert isinstance(seasons[0], Season)
            assert seasons[0].id == 19171918

    @pytest.mark.unit
    def test_get_play_by_play_success(self, sample_pbp_data):
        with requests_mock.Mocker() as m:
            m.get(
                "https://api-web.nhle.com/v1/gamecenter/2024030121/play-by-play",
                json=sample_pbp_data,
            )

            api = StatsApi()
            game = Game(
                id=2024030121,
                easternStartTime="2024-05-01T20:00:00Z",
                gameDate="2024-05-01",
                gameNumber=1,
                gameScheduleStateId=4,
                gameStateId=7,
                gameType=3,
                homeScore=3,
                homeTeamId=6,
                season=20232024,
                visitingScore=2,
                visitingTeamId=10,
            )
            result = api.get_play_by_play(game)

            assert result is not None
            assert result.id == 2024030121

    @pytest.mark.unit
    def test_get_play_by_play_not_found(self):
        with requests_mock.Mocker() as m:
            m.get(
                "https://api-web.nhle.com/v1/gamecenter/2024030121/play-by-play",
                status_code=404,
            )

            api = StatsApi()
            game = Game(
                id=2024030121,
                easternStartTime="2024-05-01T20:00:00Z",
                gameDate="2024-05-01",
                gameNumber=1,
                gameScheduleStateId=4,
                gameStateId=7,
                gameType=3,
                homeScore=3,
                homeTeamId=6,
                season=20232024,
                visitingScore=2,
                visitingTeamId=10,
            )
            with pytest.raises(NotFoundError) as exc_info:
                api.get_play_by_play(game)

            assert "Game result not found for game ID 2024030121" in str(exc_info.value)

    @pytest.mark.unit
    def test_get_shift_charts_success(self, sample_shifts_data):
        with requests_mock.Mocker() as m:
            m.get(
                "https://api.nhle.com/stats/rest/en/shiftcharts",
                json=sample_shifts_data,
            )

            api = StatsApi()
            game = Game(
                id=2024030121,
                easternStartTime="2024-05-01T20:00:00Z",
                gameDate="2024-05-01",
                gameNumber=1,
                gameScheduleStateId=4,
                gameStateId=7,
                gameType=3,
                homeScore=3,
                homeTeamId=6,
                season=20232024,
                visitingScore=2,
                visitingTeamId=10,
            )
            result = api.get_shift_charts(game)

            assert isinstance(result, list)
            assert len(result) == len(sample_shifts_data["data"])
            assert isinstance(result[0], Shift)
            assert result[0].id == 15400423
            assert result[0].game_id == 2024030121
            assert result[0].game_type == 3

    @pytest.mark.unit
    def test_get_shift_charts_not_found(self):
        with requests_mock.Mocker() as m:
            m.get("https://api.nhle.com/stats/rest/en/shiftcharts", status_code=404)

            api = StatsApi()
            game = Game(
                id=2024030121,
                easternStartTime="2024-05-01T20:00:00Z",
                gameDate="2024-05-01",
                gameNumber=1,
                gameScheduleStateId=4,
                gameStateId=7,
                gameType=3,
                homeScore=3,
                homeTeamId=6,
                season=20232024,
                visitingScore=2,
                visitingTeamId=10,
            )
            with pytest.raises(NotFoundError) as exc_info:
                api.get_shift_charts(game)

            assert "Shift chart data not found for game ID 2024030121" in str(
                exc_info.value
            )

    @pytest.mark.unit
    def test_get_shift_charts_empty_response(self):
        with requests_mock.Mocker() as m:
            m.get("https://api.nhle.com/stats/rest/en/shiftcharts", json={})

            api = StatsApi()
            game = Game(
                id=2023020001,
                easternStartTime="2023-10-10T19:00:00Z",
                gameDate="2023-10-10",
                gameNumber=1,
                gameScheduleStateId=4,
                gameStateId=7,
                gameType=2,
                homeScore=0,
                homeTeamId=1,
                season=20232024,
                visitingScore=0,
                visitingTeamId=2,
            )
            result = api.get_shift_charts(game)

            assert result == []

    @pytest.mark.unit
    def test_get_player_success(self):
        sample_player_data = {
            "playerId": 8478402,
            "isActive": True,
            "currentTeamId": 22,
            "currentTeamAbbrev": "EDM",
            "fullTeamName": {"default": "Edmonton Oilers", "fr": "Oilers d'Edmonton"},
            "teamCommonName": {"default": "Oilers"},
            "teamPlaceNameWithPreposition": {"default": "Edmonton", "fr": "d'Edmonton"},
            "firstName": {"default": "Connor"},
            "lastName": {"default": "McDavid"},
            "teamLogo": "https://assets.nhle.com/logos/nhl/svg/EDM_light.svg",
            "sweaterNumber": 97,
            "position": "C",
            "headshot": "https://assets.nhle.com/mugs/nhl/20252026/EDM/8478402.png",
            "heroImage": "https://assets.nhle.com/mugs/actionshots/1296x729/8478402.jpg",
            "heightInInches": 73,
            "heightInCentimeters": 185,
            "weightInPounds": 194,
            "weightInKilograms": 88,
            "birthDate": "1997-01-13",
            "birthCity": {"default": "Richmond Hill"},
            "birthStateProvince": {"default": "Ontario"},
            "birthCountry": "CAN",
            "shootsCatches": "L",
            "draftDetails": {
                "year": 2015,
                "teamAbbrev": "EDM",
                "round": 1,
                "pickInRound": 1,
                "overallPick": 1,
            },
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://api-web.nhle.com/v1/player/8478402/landing",
                json=sample_player_data,
            )

            api = StatsApi()
            player = api.get_player(8478402)

            assert player is not None
            assert isinstance(player, Player)
            assert player.id == 8478402
            assert player.is_active
            assert player.first_name == "Connor"
            assert player.last_name == "McDavid"
            assert player.full_team_name == "Edmonton Oilers"
            assert player.team_common_name == "Oilers"
            assert player.position == "C"
            assert player.current_team_abbrev == "EDM"
            assert player.sweater_number == 97
            assert player.birth_city == "Richmond Hill"
            assert player.birth_state_province == "Ontario"
            assert player.draft_year == 2015
            assert player.draft_overall_pick == 1
            assert player.draft_team_abbrev == "EDM"
            assert player.draft_round == 1
            assert player.draft_pick_in_round == 1

    @pytest.mark.unit
    def test_get_player_not_found(self):
        with requests_mock.Mocker() as m:
            m.get(
                "https://api-web.nhle.com/v1/player/8478402/landing",
                status_code=404,
            )

            api = StatsApi()
            with pytest.raises(NotFoundError) as exc_info:
                api.get_player(8478402)

            assert "Player not found for player ID 8478402" in str(exc_info.value)

    @pytest.mark.unit
    def test_get_player_http_error(self):
        with requests_mock.Mocker() as m:
            m.get(
                "https://api-web.nhle.com/v1/player/8478402/landing",
                status_code=500,
            )

            api = StatsApi()
            with pytest.raises(requests.exceptions.HTTPError):
                api.get_player(8478402)

    @pytest.mark.unit
    def test_get_roster_by_season_success(self):
        roster_response = {
            "forwards": [
                {
                    "id": 8479318,
                    "firstName": {"default": "Auston"},
                    "lastName": {"default": "Matthews"},
                },
                {
                    "id": 8478483,
                    "firstName": {"default": "Mitch"},
                    "lastName": {"default": "Marner"},
                },
            ],
            "defensemen": [
                {
                    "id": 8476853,
                    "firstName": {"default": "Morgan"},
                    "lastName": {"default": "Rielly"},
                },
            ],
            "goalies": [
                {
                    "id": 8479361,
                    "firstName": {"default": "Joseph"},
                    "lastName": {"default": "Woll"},
                },
            ],
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://api-web.nhle.com/v1/roster/TOR/20232024", json=roster_response
            )

            api = StatsApi()
            roster = api.get_roster_by_season("TOR", 20232024)

            assert isinstance(roster, TeamRoster)
            assert roster.forwards == [8479318, 8478483]
            assert roster.defensemen == [8476853]
            assert roster.goalies == [8479361]
            assert len(roster.all_player_ids) == 4

    @pytest.mark.unit
    def test_get_roster_by_season_empty_positions(self):
        roster_response = {
            "forwards": [],
            "defensemen": [],
            "goalies": [],
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://api-web.nhle.com/v1/roster/TOR/20232024", json=roster_response
            )

            api = StatsApi()
            roster = api.get_roster_by_season("TOR", 20232024)

            assert isinstance(roster, TeamRoster)
            assert roster.forwards == []
            assert roster.defensemen == []
            assert roster.goalies == []
            assert len(roster.all_player_ids) == 0

    @pytest.mark.unit
    def test_get_roster_by_season_missing_keys(self):
        roster_response = {}

        with requests_mock.Mocker() as m:
            m.get(
                "https://api-web.nhle.com/v1/roster/TOR/20232024", json=roster_response
            )

            api = StatsApi()
            roster = api.get_roster_by_season("TOR", 20232024)

            assert isinstance(roster, TeamRoster)
            assert roster.forwards == []
            assert roster.defensemen == []
            assert roster.goalies == []

    @pytest.mark.unit
    def test_get_roster_by_season_not_found(self):
        with requests_mock.Mocker() as m:
            m.get("https://api-web.nhle.com/v1/roster/TOR/20232024", status_code=404)

            api = StatsApi()
            with pytest.raises(NotFoundError) as exc_info:
                api.get_roster_by_season("TOR", 20232024)

            assert "Roster not found for team TOR in season 20232024" in str(
                exc_info.value
            )

    @pytest.mark.unit
    def test_get_roster_by_season_http_error(self):
        with requests_mock.Mocker() as m:
            m.get("https://api-web.nhle.com/v1/roster/TOR/20232024", status_code=500)

            api = StatsApi()
            with pytest.raises(requests.exceptions.HTTPError):
                api.get_roster_by_season("TOR", 20232024)

    @pytest.mark.unit
    def test_get_retries_on_429_then_succeeds(self, mocker):
        """Test _get retries after a 429 and returns the successful response."""
        mocker.patch("icetime.api.time.sleep")
        url = "https://api.nhle.com/stats/rest/en/team"
        with requests_mock.Mocker() as m:
            m.get(
                url,
                [
                    {"status_code": 429, "headers": {"Retry-After": "0"}},
                    {"json": {"data": []}, "status_code": 200},
                ],
            )

            api = StatsApi(request_delay=0)
            response = api._get(url)

            assert response.status_code == 200
            assert m.call_count == 2

    @pytest.mark.unit
    def test_get_retries_up_to_ten_times_on_429(self, mocker):
        """Test _get raises after exhausting 10 retries on 429."""
        mocker.patch("icetime.api.time.sleep")
        url = "https://api.nhle.com/stats/rest/en/team"
        with requests_mock.Mocker() as m:
            m.get(url, status_code=429, headers={"Retry-After": "0"})

            api = StatsApi(request_delay=0)
            with pytest.raises(requests.exceptions.HTTPError):
                api._get(url)

            assert m.call_count == 10

    @pytest.mark.unit
    def test_get_uses_retry_after_header(self, mocker):
        """Test _get respects the Retry-After header when larger than backoff."""
        mock_sleep = mocker.patch("icetime.api.time.sleep")
        url = "https://api.nhle.com/stats/rest/en/team"
        with requests_mock.Mocker() as m:
            m.get(
                url,
                [
                    {"status_code": 429, "headers": {"Retry-After": "30"}},
                    {"json": {"data": []}, "status_code": 200},
                ],
            )

            api = StatsApi(request_delay=0)
            api._get(url)

            mock_sleep.assert_called_once_with(30)

    @pytest.mark.unit
    def test_get_uses_backoff_when_retry_after_is_zero(self, mocker):
        """Test _get uses exponential backoff when Retry-After is 0 or absent."""
        mock_sleep = mocker.patch("icetime.api.time.sleep")
        url = "https://api.nhle.com/stats/rest/en/team"
        with requests_mock.Mocker() as m:
            m.get(
                url,
                [
                    {"status_code": 429, "headers": {"Retry-After": "0"}},
                    {"status_code": 429, "headers": {"Retry-After": "0"}},
                    {"json": {"data": []}, "status_code": 200},
                ],
            )

            api = StatsApi(request_delay=0)
            api._get(url)

            assert mock_sleep.call_count == 2
            mock_sleep.assert_any_call(2)
            mock_sleep.assert_any_call(4)

    @pytest.mark.unit
    def test_get_retries_on_connection_error_then_succeeds(self, mocker):
        """Test _get retries after a ConnectionError and returns the successful response."""
        mock_sleep = mocker.patch("icetime.api.time.sleep")
        url = "https://api.nhle.com/stats/rest/en/team"
        with requests_mock.Mocker() as m:
            m.get(
                url,
                [
                    {"exc": requests.exceptions.ConnectionError("reset")},
                    {"json": {"data": []}, "status_code": 200},
                ],
            )

            api = StatsApi(request_delay=0)
            response = api._get(url)

            assert response.status_code == 200
            assert m.call_count == 2
            mock_sleep.assert_called_once_with(2)

    @pytest.mark.unit
    def test_get_raises_after_exhausting_connection_error_retries(self, mocker):
        """Test _get raises ConnectionError after exhausting all retries."""
        mocker.patch("icetime.api.time.sleep")
        url = "https://api.nhle.com/stats/rest/en/team"
        with requests_mock.Mocker() as m:
            m.get(url, exc=requests.exceptions.ConnectionError("reset"))

            api = StatsApi(request_delay=0)
            with pytest.raises(requests.exceptions.ConnectionError):
                api._get(url)

            assert m.call_count == 10

    @pytest.mark.unit
    def test_get_play_by_play_retries_on_429(self, mocker):
        """Test get_play_by_play retries on 429 before succeeding."""
        mocker.patch("icetime.api.time.sleep")
        game = Game(
            id=2024030121,
            easternStartTime="2024-05-01T20:00:00Z",
            gameDate="2024-05-01",
            gameNumber=1,
            gameScheduleStateId=4,
            gameStateId=7,
            gameType=3,
            homeScore=3,
            homeTeamId=6,
            season=20232024,
            visitingScore=2,
            visitingTeamId=10,
        )
        url = "https://api-web.nhle.com/v1/gamecenter/2024030121/play-by-play"
        with requests_mock.Mocker() as m:
            m.get(
                url,
                [
                    {"status_code": 429, "headers": {"Retry-After": "0"}},
                    {"json": self._pbp_payload(), "status_code": 200},
                ],
            )

            api = StatsApi(request_delay=0)
            result = api.get_play_by_play(game)

            assert result is not None
            assert m.call_count == 2

    def _pbp_payload(self):
        return {
            "id": 2024030121,
            "season": 20232024,
            "gameType": 3,
            "gameDate": "2024-05-01",
            "venue": {"default": "TD Garden"},
            "venueLocation": {"default": "Boston"},
            "startTimeUTC": "2024-05-02T00:00:00Z",
            "easternUTCOffset": "-04:00",
            "venueUTCOffset": "-04:00",
            "gameState": "OFF",
            "gameScheduleState": "OK",
            "periodDescriptor": {"number": 3, "periodType": "REG"},
            "awayTeam": {
                "id": 10,
                "commonName": {"default": "Leafs"},
                "abbrev": "TOR",
                "logo": "https://example.com/tor.svg",
                "darkLogo": "https://example.com/tor_dark.svg",
                "score": 2,
                "sog": 25,
            },
            "homeTeam": {
                "id": 6,
                "commonName": {"default": "Bruins"},
                "abbrev": "BOS",
                "logo": "https://example.com/bos.svg",
                "darkLogo": "https://example.com/bos_dark.svg",
                "score": 3,
                "sog": 30,
            },
            "clock": {"timeRemaining": "00:00"},
        }
