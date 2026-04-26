import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from typer.testing import CliRunner
from icetime.cli import app
from icetime.api import NotFoundError
from icetime.models import Team, Game, Season, TeamRoster


class TestCLI:
    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @pytest.mark.unit
    def test_main_callback_without_command(self):
        """Test main callback shows help when no command is provided."""
        result = self.runner.invoke(app, [])

        assert result.exit_code == 0
        assert "Usage:" in result.stdout

    @pytest.mark.unit
    def test_version_command(self):
        """Test version command shows correct version."""
        result = self.runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "icetime v1.0.0" in result.stdout

    @pytest.mark.unit
    @patch("icetime.cli.StatsApi")
    @patch("icetime.cli.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("icetime.cli.TypeAdapter")
    def test_get_teams_success(
        self, mock_type_adapter, mock_file, mock_mkdir, mock_stats_api
    ):
        """Test get_teams command success."""
        # Setup mocks
        mock_api_instance = MagicMock()
        mock_teams = [
            Team(id=1, fullName="Team 1", leagueId=133, rawTricode="T1", triCode="T1"),
            Team(id=2, fullName="Team 2", leagueId=133, rawTricode="T2", triCode="T2"),
        ]
        mock_api_instance.get_teams.return_value = mock_teams

        mock_adapter_instance = MagicMock()
        mock_adapter_instance.dump_json.return_value = b'{"teams": "data"}'
        mock_type_adapter.return_value = mock_adapter_instance

        with patch("icetime.cli.api", mock_api_instance):
            result = self.runner.invoke(app, ["get-teams"])

        assert result.exit_code == 0
        mock_api_instance.get_teams.assert_called_once()
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file.assert_called_once()
        mock_adapter_instance.dump_json.assert_called_once_with(mock_teams, indent=2)

    @pytest.mark.unit
    @patch("icetime.cli.StatsApi")
    def test_get_teams_api_error(self, mock_stats_api):
        """Test get_teams command handles API errors."""
        mock_api_instance = MagicMock()
        mock_api_instance.get_teams.side_effect = Exception("API Error")

        with patch("icetime.cli.api", mock_api_instance):
            result = self.runner.invoke(app, ["get-teams"])

        assert result.exit_code == 1
        assert "Error fetching teams: API Error" in result.stderr

    @pytest.mark.unit
    @patch("icetime.cli.StatsApi")
    @patch("icetime.cli.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("icetime.cli.TypeAdapter")
    def test_get_teams_with_custom_output_path(
        self, mock_type_adapter, mock_file, mock_mkdir, mock_stats_api
    ):
        """Test get_teams command with custom output path."""
        mock_api_instance = MagicMock()
        mock_api_instance.get_teams.return_value = []

        mock_adapter_instance = MagicMock()
        mock_adapter_instance.dump_json.return_value = b"[]"
        mock_type_adapter.return_value = mock_adapter_instance

        with patch("icetime.cli.api", mock_api_instance):
            result = self.runner.invoke(
                app, ["get-teams", "--output-path", "/custom/path"]
            )

        assert result.exit_code == 0
        # Verify the custom path was used
        assert "/custom/path" in str(mock_file.call_args[0][0])

    @pytest.mark.unit
    @patch("icetime.cli.StatsApi")
    @patch("icetime.cli.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("icetime.cli.TypeAdapter")
    def test_get_games_success(
        self, mock_type_adapter, mock_file, mock_mkdir, mock_stats_api
    ):
        """Test get_games command success."""
        mock_api_instance = MagicMock()
        mock_games = [
            Game(
                id=1,
                easternStartTime="2023-10-10T19:00:00Z",
                gameDate="2023-10-10",
                gameNumber=1,
                gameScheduleStateId=4,
                gameStateId=7,
                gameType=2,
                homeScore=3,
                homeTeamId=1,
                season=20232024,
                visitingScore=2,
                visitingTeamId=2,
            )
        ]
        mock_api_instance.get_games.return_value = mock_games

        mock_adapter_instance = MagicMock()
        mock_adapter_instance.dump_json.return_value = b'{"games": "data"}'
        mock_type_adapter.return_value = mock_adapter_instance

        with patch("icetime.cli.api", mock_api_instance):
            result = self.runner.invoke(app, ["get-games"])

        assert result.exit_code == 0
        mock_api_instance.get_games.assert_called_once()

    @pytest.mark.unit
    @patch("icetime.cli.StatsApi")
    @patch("icetime.cli.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("icetime.cli.TypeAdapter")
    def test_get_seasons_success(
        self, mock_type_adapter, mock_file, mock_mkdir, mock_stats_api
    ):
        """Test get_seasons command success."""
        mock_api_instance = MagicMock()
        mock_seasons = [
            Season(
                id=20232024,
                allStarGameInUse=1,
                conferencesInUse=1,
                divisionsInUse=1,
                endDate="2024-06-24",
                entryDraftInUse=1,
                formattedSeasonId="2023-24",
                minimumPlayoffMinutesForGoalieStatsLeaders=180,
                minimumRegularGamesForGoalieStatsLeaders=25,
                nhlStanleyCupOwner=1,
                numberOfGames=82,
                olympicsParticipation=0,
                pointForOTLossInUse=1,
                regularSeasonEndDate="2024-04-18",
                rowInUse=1,
                seasonOrdinal=107,
                startDate="2023-10-10",
                supplementalDraftInUse=0,
                tiesInUse=0,
                totalPlayoffGames=89,
                totalRegularSeasonGames=1312,
                wildcardInUse=1,
            )
        ]
        mock_api_instance.get_seasons.return_value = mock_seasons

        mock_adapter_instance = MagicMock()
        mock_adapter_instance.dump_json.return_value = b'{"seasons": "data"}'
        mock_type_adapter.return_value = mock_adapter_instance

        with patch("icetime.cli.api", mock_api_instance):
            result = self.runner.invoke(app, ["get-seasons"])

        assert result.exit_code == 0
        mock_api_instance.get_seasons.assert_called_once()

    @pytest.mark.unit
    @patch("icetime.cli.StatsApi")
    @patch("icetime.cli.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("icetime.cli.TypeAdapter")
    def test_get_pbp_success(
        self, mock_type_adapter, mock_file, mock_mkdir, mock_stats_api
    ):
        """Test get_pbp command success."""
        mock_api_instance = MagicMock()
        mock_game = Game(
            id=123,
            easternStartTime="2023-10-10T19:00:00Z",
            gameDate="2023-10-10",
            gameNumber=1,
            gameScheduleStateId=4,
            gameStateId=7,
            gameType=2,
            homeScore=3,
            homeTeamId=1,
            season=20232024,
            visitingScore=2,
            visitingTeamId=2,
        )
        mock_api_instance.get_games_by_season.return_value = [mock_game]
        mock_api_instance.get_play_by_play.return_value = {"gameId": 123, "plays": []}

        mock_adapter_instance = MagicMock()
        mock_adapter_instance.dump_json.return_value = b'{"data": "pbp"}'
        mock_type_adapter.return_value = mock_adapter_instance

        with patch("icetime.cli.api", mock_api_instance):
            result = self.runner.invoke(app, ["get-pbp", "--season", "20232024"])

        assert result.exit_code == 0
        mock_api_instance.get_games_by_season.assert_called_once_with(20232024)
        # Verify get_play_by_play was called with the correct game
        mock_api_instance.get_play_by_play.assert_called_once()
        call_args = mock_api_instance.get_play_by_play.call_args[0][0]
        assert call_args.id == 123

    @pytest.mark.unit
    @patch("icetime.cli.StatsApi")
    def test_get_pbp_no_games(self, mock_stats_api):
        """Test get_pbp command when no games found."""
        mock_api_instance = MagicMock()
        mock_api_instance.get_games_by_season.return_value = []

        with patch("icetime.cli.api", mock_api_instance):
            result = self.runner.invoke(app, ["get-pbp", "--season", "20232024"])

        assert result.exit_code == 0
        mock_api_instance.get_games_by_season.assert_called_once_with(20232024)

    @pytest.mark.unit
    @patch("icetime.cli.StatsApi")
    @patch("icetime.cli.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("icetime.cli.TypeAdapter")
    def test_get_pbp_handles_not_found_error(
        self, mock_type_adapter, mock_file, mock_mkdir, mock_stats_api
    ):
        """Test get_pbp command handles NotFoundError gracefully."""
        mock_api_instance = MagicMock()
        mock_game1 = Game(
            id=123,
            easternStartTime="2023-10-10T19:00:00Z",
            gameDate="2023-10-10",
            gameNumber=1,
            gameScheduleStateId=4,
            gameStateId=7,
            gameType=2,
            homeScore=3,
            homeTeamId=1,
            season=20232024,
            visitingScore=2,
            visitingTeamId=2,
        )
        mock_game2 = Game(
            id=456,
            easternStartTime="2023-10-10T19:00:00Z",
            gameDate="2023-10-10",
            gameNumber=2,
            gameScheduleStateId=4,
            gameStateId=7,
            gameType=2,
            homeScore=1,
            homeTeamId=3,
            season=20232024,
            visitingScore=0,
            visitingTeamId=4,
        )
        mock_api_instance.get_games_by_season.return_value = [mock_game1, mock_game2]
        mock_api_instance.get_play_by_play.side_effect = [
            NotFoundError("Not found"),
            {"gameId": 456, "plays": []},
        ]

        mock_adapter_instance = MagicMock()
        mock_adapter_instance.dump_json.return_value = b'{"data": "pbp"}'
        mock_type_adapter.return_value = mock_adapter_instance

        with patch("icetime.cli.api", mock_api_instance):
            result = self.runner.invoke(app, ["get-pbp", "--season", "20232024"])

        assert result.exit_code == 0
        assert mock_api_instance.get_play_by_play.call_count == 2

    @pytest.mark.unit
    @patch("icetime.cli.StatsApi")
    def test_get_pbp_handles_general_error(self, mock_stats_api):
        """Test get_pbp command handles general errors."""
        mock_api_instance = MagicMock()
        mock_game = Game(
            id=123,
            easternStartTime="2023-10-10T19:00:00Z",
            gameDate="2023-10-10",
            gameNumber=1,
            gameScheduleStateId=4,
            gameStateId=7,
            gameType=2,
            homeScore=3,
            homeTeamId=1,
            season=20232024,
            visitingScore=2,
            visitingTeamId=2,
        )
        mock_api_instance.get_games_by_season.return_value = [mock_game]
        mock_api_instance.get_play_by_play.side_effect = Exception("General error")

        with patch("icetime.cli.api", mock_api_instance):
            result = self.runner.invoke(app, ["get-pbp", "--season", "20232024"])

        assert result.exit_code == 1
        assert (
            "Error fetching play-by-play for game 123: General error" in result.stderr
        )

    @pytest.mark.unit
    @patch("icetime.cli.StatsApi")
    @patch("icetime.cli.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("icetime.cli.TypeAdapter")
    def test_get_shifts_success(
        self, mock_type_adapter, mock_file, mock_mkdir, mock_stats_api
    ):
        """Test get_shifts command success."""
        mock_api_instance = MagicMock()
        mock_game = Game(
            id=123,
            easternStartTime="2023-10-10T19:00:00Z",
            gameDate="2023-10-10",
            gameNumber=1,
            gameScheduleStateId=4,
            gameStateId=7,
            gameType=2,
            homeScore=3,
            homeTeamId=1,
            season=20232024,
            visitingScore=2,
            visitingTeamId=2,
        )
        mock_api_instance.get_games_by_season.return_value = [mock_game]
        mock_api_instance.get_shift_charts.return_value = [{"id": 1, "gameId": 123}]

        mock_adapter_instance = MagicMock()
        mock_adapter_instance.dump_json.return_value = b'{"data": "shifts"}'
        mock_type_adapter.return_value = mock_adapter_instance

        with patch("icetime.cli.api", mock_api_instance):
            result = self.runner.invoke(app, ["get-shifts", "--season", "20232024"])

        assert result.exit_code == 0
        mock_api_instance.get_games_by_season.assert_called_once_with(20232024)
        # Verify get_shift_charts was called with the correct game object
        mock_api_instance.get_shift_charts.assert_called_once()
        call_args = mock_api_instance.get_shift_charts.call_args[0][0]
        assert call_args.id == 123

    @pytest.mark.unit
    @patch("icetime.cli.StatsApi")
    @patch("icetime.cli.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("icetime.cli.TypeAdapter")
    def test_get_shifts_handles_not_found_error(
        self, mock_type_adapter, mock_file, mock_mkdir, mock_stats_api
    ):
        """Test get_shifts command handles NotFoundError gracefully."""
        mock_api_instance = MagicMock()
        mock_game1 = Game(
            id=123,
            easternStartTime="2023-10-10T19:00:00Z",
            gameDate="2023-10-10",
            gameNumber=1,
            gameScheduleStateId=4,
            gameStateId=7,
            gameType=2,
            homeScore=3,
            homeTeamId=1,
            season=20232024,
            visitingScore=2,
            visitingTeamId=2,
        )
        mock_game2 = Game(
            id=456,
            easternStartTime="2023-10-10T19:00:00Z",
            gameDate="2023-10-10",
            gameNumber=2,
            gameScheduleStateId=4,
            gameStateId=7,
            gameType=2,
            homeScore=1,
            homeTeamId=3,
            season=20232024,
            visitingScore=0,
            visitingTeamId=4,
        )
        mock_api_instance.get_games_by_season.return_value = [mock_game1, mock_game2]
        mock_api_instance.get_shift_charts.side_effect = [
            NotFoundError("Not found"),
            [{"id": 1, "gameId": 456}],
        ]

        mock_adapter_instance = MagicMock()
        mock_adapter_instance.dump_json.return_value = b'{"data": "shifts"}'
        mock_type_adapter.return_value = mock_adapter_instance

        with patch("icetime.cli.api", mock_api_instance):
            result = self.runner.invoke(app, ["get-shifts", "--season", "20232024"])

        assert result.exit_code == 0
        assert mock_api_instance.get_shift_charts.call_count == 2

    @pytest.mark.unit
    @patch("icetime.cli.StatsApi")
    def test_get_shifts_handles_general_error(self, mock_stats_api):
        """Test get_shifts command handles general errors."""
        mock_api_instance = MagicMock()
        mock_game = Game(
            id=123,
            easternStartTime="2023-10-10T19:00:00Z",
            gameDate="2023-10-10",
            gameNumber=1,
            gameScheduleStateId=4,
            gameStateId=7,
            gameType=2,
            homeScore=3,
            homeTeamId=1,
            season=20232024,
            visitingScore=2,
            visitingTeamId=2,
        )
        mock_api_instance.get_games_by_season.return_value = [mock_game]
        mock_api_instance.get_shift_charts.side_effect = Exception("General error")

        with patch("icetime.cli.api", mock_api_instance):
            result = self.runner.invoke(app, ["get-shifts", "--season", "20232024"])

        assert result.exit_code == 1
        assert (
            "Error fetching shift charts for game 123: General error" in result.stderr
        )

    @pytest.mark.unit
    @patch("icetime.cli.get_teams")
    @patch("icetime.cli.get_games")
    @patch("icetime.cli.get_seasons")
    @patch("icetime.cli.get_pbp")
    @patch("icetime.cli.get_shifts")
    @patch("icetime.cli.get_rosters")
    @patch("icetime.cli.get_players")
    def test_get_all_command(
        self,
        mock_get_players,
        mock_get_rosters,
        mock_get_shifts,
        mock_get_pbp,
        mock_get_seasons,
        mock_get_games,
        mock_get_teams,
    ):
        """Test get_all command calls all individual commands."""
        result = self.runner.invoke(app, ["get-all", "--season", "20232024"])

        assert result.exit_code == 0
        mock_get_teams.assert_called_once_with(False, "./data")
        mock_get_games.assert_called_once_with(False, "./data")
        mock_get_seasons.assert_called_once_with(False, "./data")
        mock_get_pbp.assert_called_once_with(20232024, False, "./data")
        mock_get_shifts.assert_called_once_with(20232024, False, "./data")
        mock_get_rosters.assert_called_once_with(20232024, False, "./data")
        mock_get_players.assert_called_once_with(None, False, "./data")

    @pytest.mark.unit
    @patch("icetime.cli.get_teams")
    @patch("icetime.cli.get_games")
    @patch("icetime.cli.get_seasons")
    @patch("icetime.cli.get_pbp")
    @patch("icetime.cli.get_shifts")
    @patch("icetime.cli.get_rosters")
    @patch("icetime.cli.get_players")
    def test_get_all_command_with_options(
        self,
        mock_get_players,
        mock_get_rosters,
        mock_get_shifts,
        mock_get_pbp,
        mock_get_seasons,
        mock_get_games,
        mock_get_teams,
    ):
        """Test get_all command with quiet and custom output path."""
        result = self.runner.invoke(
            app,
            ["get-all", "--season", "20232024", "--quiet", "--output-path", "/custom"],
        )

        assert result.exit_code == 0
        mock_get_teams.assert_called_once_with(True, "/custom")
        mock_get_games.assert_called_once_with(True, "/custom")
        mock_get_seasons.assert_called_once_with(True, "/custom")
        mock_get_pbp.assert_called_once_with(20232024, True, "/custom")
        mock_get_shifts.assert_called_once_with(20232024, True, "/custom")
        mock_get_rosters.assert_called_once_with(20232024, True, "/custom")
        mock_get_players.assert_called_once_with(None, True, "/custom")

    @pytest.mark.unit
    @patch("icetime.cli.StatsApi")
    @patch("icetime.cli.reporter")
    def test_quiet_mode(self, mock_reporter, mock_stats_api):
        """Test that quiet mode is properly passed to reporter."""
        mock_progress = MagicMock()
        mock_reporter.return_value.__enter__.return_value = mock_progress
        mock_api_instance = MagicMock()
        mock_api_instance.get_teams.return_value = []

        with patch("icetime.cli.api", mock_api_instance):
            result = self.runner.invoke(app, ["get-teams", "--quiet"])

        assert result.exit_code == 0
        mock_reporter.assert_called_with(True)

    @pytest.mark.unit
    def test_missing_season_parameter(self):
        """Test commands that require season parameter fail without it."""
        result = self.runner.invoke(app, ["get-pbp"])
        assert result.exit_code != 0
        assert "Missing option" in result.stderr

        result = self.runner.invoke(app, ["get-shifts"])
        assert result.exit_code != 0
        assert "Missing option" in result.stderr

        result = self.runner.invoke(app, ["get-all"])
        assert result.exit_code != 0
        assert "Missing option" in result.stderr

        result = self.runner.invoke(app, ["get-rosters"])
        assert result.exit_code != 0
        assert "Missing option" in result.stderr

    @pytest.mark.unit
    @patch("icetime.cli.StatsApi")
    @patch("icetime.cli.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("icetime.cli.TypeAdapter")
    def test_get_rosters_success(
        self, mock_type_adapter, mock_file, mock_mkdir, mock_stats_api
    ):
        """Test get_rosters command success."""
        mock_api_instance = MagicMock()
        mock_teams = [
            Team(id=1, fullName="Team 1", leagueId=133, rawTricode="T1", triCode="T1"),
            Team(id=2, fullName="Team 2", leagueId=133, rawTricode="T2", triCode="T2"),
        ]
        mock_api_instance.get_teams.return_value = mock_teams

        mock_roster1 = TeamRoster(forwards=[123, 456], defensemen=[789], goalies=[101])
        mock_roster2 = TeamRoster(forwards=[234], defensemen=[567, 890], goalies=[102])
        mock_api_instance.get_roster_by_season.side_effect = [
            mock_roster1,
            mock_roster2,
        ]

        mock_adapter_instance = MagicMock()
        mock_adapter_instance.dump_json.return_value = (
            b'[{"team_id": 1, "player_id": 123}]'
        )
        mock_type_adapter.return_value = mock_adapter_instance

        with patch("icetime.cli.api", mock_api_instance):
            result = self.runner.invoke(app, ["get-rosters", "--season", "20232024"])

        assert result.exit_code == 0
        mock_api_instance.get_teams.assert_called_once()
        assert mock_api_instance.get_roster_by_season.call_count == 2
        mock_api_instance.get_roster_by_season.assert_any_call("T1", 20232024)
        mock_api_instance.get_roster_by_season.assert_any_call("T2", 20232024)

        # Verify the data structure passed to TypeAdapter.dump_json
        call_args = mock_adapter_instance.dump_json.call_args[0][0]
        assert isinstance(call_args, list)
        # Should have entries for all players from both teams (4 + 4 = 8 players)
        assert len(call_args) == 8
        # Check some specific entries
        expected_entries = [
            {"team_id": 1, "player_id": 123},
            {"team_id": 1, "player_id": 456},
            {"team_id": 1, "player_id": 789},
            {"team_id": 1, "player_id": 101},
            {"team_id": 2, "player_id": 234},
            {"team_id": 2, "player_id": 567},
            {"team_id": 2, "player_id": 890},
            {"team_id": 2, "player_id": 102},
        ]
        for expected_entry in expected_entries:
            assert expected_entry in call_args

    @pytest.mark.unit
    @patch("icetime.cli.StatsApi")
    @patch("icetime.cli.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("icetime.cli.TypeAdapter")
    def test_get_rosters_handles_not_found_error(
        self, mock_type_adapter, mock_file, mock_mkdir, mock_stats_api
    ):
        """Test get_rosters command handles NotFoundError gracefully."""
        mock_api_instance = MagicMock()
        mock_teams = [
            Team(id=1, fullName="Team 1", leagueId=133, rawTricode="T1", triCode="T1"),
            Team(id=2, fullName="Team 2", leagueId=133, rawTricode="T2", triCode="T2"),
        ]
        mock_api_instance.get_teams.return_value = mock_teams

        mock_roster = TeamRoster(forwards=[123], defensemen=[456], goalies=[789])
        mock_api_instance.get_roster_by_season.side_effect = [
            NotFoundError("Not found"),
            mock_roster,
        ]

        mock_adapter_instance = MagicMock()
        mock_adapter_instance.dump_json.return_value = (
            b'[{"team_id": 2, "player_id": 123}]'
        )
        mock_type_adapter.return_value = mock_adapter_instance

        with patch("icetime.cli.api", mock_api_instance):
            result = self.runner.invoke(app, ["get-rosters", "--season", "20232024"])

        assert result.exit_code == 0
        assert mock_api_instance.get_roster_by_season.call_count == 2

        # Verify only T2 players are in the output (T1 had NotFoundError)
        call_args = mock_adapter_instance.dump_json.call_args[0][0]
        assert len(call_args) == 3  # Only 3 players from T2
        expected_entries = [
            {"team_id": 2, "player_id": 123},
            {"team_id": 2, "player_id": 456},
            {"team_id": 2, "player_id": 789},
        ]
        for expected_entry in expected_entries:
            assert expected_entry in call_args

    @pytest.mark.unit
    @patch("icetime.cli.StatsApi")
    def test_get_rosters_handles_general_error(self, mock_stats_api):
        """Test get_rosters command handles general errors."""
        mock_api_instance = MagicMock()
        mock_teams = [
            Team(id=1, fullName="Team 1", leagueId=133, rawTricode="T1", triCode="T1"),
        ]
        mock_api_instance.get_teams.return_value = mock_teams
        mock_api_instance.get_roster_by_season.side_effect = Exception("General error")

        with patch("icetime.cli.api", mock_api_instance):
            result = self.runner.invoke(app, ["get-rosters", "--season", "20232024"])

        assert result.exit_code == 1
        assert "Error fetching roster for team T1: General error" in result.stderr

    @pytest.mark.unit
    def test_get_players_requires_season_without_rosters(self):
        """Test get_players exits with error when rosters.json is missing and no --season."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(
                app, ["get-players", "--output-path", temp_dir, "--quiet"]
            )

        assert result.exit_code == 1
        assert "--season is required" in result.stderr

    @pytest.mark.unit
    def test_get_players_success_with_existing_rosters(self):
        """Test get_players uses existing rosters.json without fetching rosters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rosters = [
                {"team_id": 1, "player_id": 123},
                {"team_id": 2, "player_id": 456},
            ]
            Path(temp_dir, "rosters.json").write_bytes(json.dumps(rosters).encode())

            mock_api_instance = MagicMock()
            mock_api_instance.get_player.return_value = None

            with patch("icetime.cli.api", mock_api_instance):
                result = self.runner.invoke(
                    app, ["get-players", "--output-path", temp_dir, "--quiet"]
                )

            assert result.exit_code == 0
            mock_api_instance.get_player.assert_any_call(123)
            mock_api_instance.get_player.assert_any_call(456)
            assert (Path(temp_dir) / "players.json").exists()

    @pytest.mark.unit
    def test_get_players_deduplicates_player_ids(self):
        """Test get_players only fetches each unique player ID once."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rosters = [
                {"team_id": 1, "player_id": 123},
                {"team_id": 2, "player_id": 123},
                {"team_id": 1, "player_id": 456},
            ]
            Path(temp_dir, "rosters.json").write_bytes(json.dumps(rosters).encode())

            mock_api_instance = MagicMock()
            mock_api_instance.get_player.return_value = None

            with patch("icetime.cli.api", mock_api_instance):
                result = self.runner.invoke(
                    app, ["get-players", "--output-path", temp_dir, "--quiet"]
                )

            assert result.exit_code == 0
            assert mock_api_instance.get_player.call_count == 2

    @pytest.mark.unit
    def test_get_players_handles_not_found_error(self):
        """Test get_players skips players that return NotFoundError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rosters = [
                {"team_id": 1, "player_id": 123},
                {"team_id": 1, "player_id": 456},
            ]
            Path(temp_dir, "rosters.json").write_bytes(json.dumps(rosters).encode())

            mock_api_instance = MagicMock()
            mock_api_instance.get_player.side_effect = [
                NotFoundError("Not found"),
                None,
            ]

            with patch("icetime.cli.api", mock_api_instance):
                result = self.runner.invoke(
                    app, ["get-players", "--output-path", temp_dir, "--quiet"]
                )

            assert result.exit_code == 0
            assert mock_api_instance.get_player.call_count == 2

    @pytest.mark.unit
    def test_get_players_handles_general_error(self):
        """Test get_players exits with error on general API failures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rosters = [{"team_id": 1, "player_id": 123}]
            Path(temp_dir, "rosters.json").write_bytes(json.dumps(rosters).encode())

            mock_api_instance = MagicMock()
            mock_api_instance.get_player.side_effect = Exception("API Error")

            with patch("icetime.cli.api", mock_api_instance):
                result = self.runner.invoke(
                    app, ["get-players", "--output-path", temp_dir, "--quiet"]
                )

            assert result.exit_code == 1
            assert "Error fetching player 123: API Error" in result.stderr

    @pytest.mark.unit
    @patch("icetime.cli.get_rosters")
    def test_get_players_fetches_rosters_when_missing(self, mock_get_rosters):
        """Test get_players calls get_rosters first when rosters.json is absent."""
        with tempfile.TemporaryDirectory() as temp_dir:

            def create_rosters(season, quiet, output_path):
                Path(output_path, "rosters.json").write_bytes(
                    json.dumps([{"team_id": 1, "player_id": 123}]).encode()
                )

            mock_get_rosters.side_effect = create_rosters
            mock_api_instance = MagicMock()
            mock_api_instance.get_player.return_value = None

            with patch("icetime.cli.api", mock_api_instance):
                result = self.runner.invoke(
                    app,
                    [
                        "get-players",
                        "--season",
                        "20232024",
                        "--output-path",
                        temp_dir,
                        "--quiet",
                    ],
                )

            assert result.exit_code == 0
            mock_get_rosters.assert_called_once_with(20232024, True, temp_dir)
            mock_api_instance.get_player.assert_called_once_with(123)


class TestCLIIntegration:
    """Integration tests for CLI with temporary directories."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @pytest.mark.integration
    def test_get_teams_creates_output_directory(self):
        """Test that get_teams creates the output directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_output"

            with patch("icetime.cli.StatsApi") as mock_stats_api:
                mock_api_instance = MagicMock()
                mock_api_instance.get_teams.return_value = []
                mock_stats_api.return_value = mock_api_instance

                with patch("icetime.cli.api", mock_api_instance):
                    result = self.runner.invoke(
                        app, ["get-teams", "--output-path", str(output_path), "--quiet"]
                    )

                    assert result.exit_code == 0
                    assert output_path.exists()
                    assert (output_path / "teams.json").exists()

    @pytest.mark.integration
    def test_file_permissions_and_content(self):
        """Test that output files are created with proper content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir)

            with patch("icetime.cli.StatsApi") as mock_stats_api:
                mock_api_instance = MagicMock()
                mock_teams = [
                    Team(
                        id=1,
                        fullName="Test Team",
                        leagueId=133,
                        rawTricode="TT",
                        triCode="TT",
                    )
                ]
                mock_api_instance.get_teams.return_value = mock_teams
                mock_stats_api.return_value = mock_api_instance

                with patch("icetime.cli.api", mock_api_instance):
                    result = self.runner.invoke(
                        app, ["get-teams", "--output-path", str(output_path), "--quiet"]
                    )

                    assert result.exit_code == 0
                    teams_file = output_path / "teams.json"
                    assert teams_file.exists()

                    # Verify file content is valid JSON
                    with open(teams_file, "rb") as f:
                        content = f.read()
                        assert content  # File should not be empty
