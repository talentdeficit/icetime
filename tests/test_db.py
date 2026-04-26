import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from icetime.cli import app
from icetime.db import load_to_sqlite


TEAMS_DATA = [
    {
        "id": 6,
        "franchise_id": 6,
        "full_name": "Boston Bruins",
        "league_id": 133,
        "raw_tricode": "BOS",
        "tri_code": "BOS",
    }
]

GAMES_DATA = [
    {
        "id": 2023020001,
        "eastern_start_time": "19:00",
        "game_date": "2023-10-10",
        "game_number": 1,
        "game_schedule_state_id": 4,
        "game_state_id": 7,
        "game_type": 2,
        "home_score": 3,
        "home_team_id": 6,
        "period": None,
        "season": 20232024,
        "visiting_score": 2,
        "visiting_team_id": 8,
    }
]

SEASONS_DATA = [
    {
        "id": 20232024,
        "name": "20232024",
        "all_star_game_in_use": 0,
        "conferences_in_use": 1,
        "divisions_in_use": 1,
        "end_date": "2024-06-24",
        "entry_draft_in_use": 1,
        "formatted_season_id": "2023-24",
        "minimum_playoff_minutes_for_goalie_stats_leaders": 180,
        "minimum_regular_games_for_goalie_stats_leaders": 25,
        "nhl_stanley_cup_owner": 1,
        "number_of_games": 82,
        "olympics_participation": 0,
        "point_for_ot_loss_in_use": 1,
        "preseason_startdate": None,
        "regular_season_end_date": "2024-04-18",
        "row_in_use": 1,
        "season_ordinal": 107,
        "start_date": "2023-10-10",
        "supplemental_draft_in_use": 0,
        "ties_in_use": 0,
        "total_playoff_games": 89,
        "total_regular_season_games": 1312,
        "wildcard_in_use": 1,
    }
]

PBP_DATA = [
    {
        "id": 2023020001,
        "season": 20232024,
        "game_type": 2,
        "game_date": "2023-10-10",
        "venue": "TD Garden",
        "venue_location": "Boston, MA",
        "start_time_utc": "2023-10-10T23:00:00Z",
        "eastern_utc_offset": "-04:00",
        "venue_utc_offset": "-04:00",
        "game_state": "OFF",
        "game_schedule_state": "OK",
        "period": 3,
        "period_type": "REG",
        "away_team_id": 8,
        "away_team_name": "Canadiens",
        "away_team_abbreviation": "MTL",
        "away_team_logo": "https://assets.nhle.com/logos/nhl/svg/MTL_light.svg",
        "away_team_dark_logo": "https://assets.nhle.com/logos/nhl/svg/MTL_dark.svg",
        "home_team_id": 6,
        "home_team_name": "Bruins",
        "home_team_abbreviation": "BOS",
        "home_team_logo": "https://assets.nhle.com/logos/nhl/svg/BOS_light.svg",
        "home_team_dark_logo": "https://assets.nhle.com/logos/nhl/svg/BOS_dark.svg",
        "away_score": 1,
        "home_score": 3,
        "away_shots": 28,
        "home_shots": 35,
        "time_remaining": "00:00",
    }
]

SHIFTS_DATA = [
    {
        "id": 1,
        "detail_code": None,
        "duration": "00:45",
        "end_time": "01:02",
        "event_description": None,
        "event_details": None,
        "event_number": None,
        "first_name": "Brad",
        "game_id": 2023020001,
        "hex_value": "#FCB514",
        "last_name": "Marchand",
        "period": 1,
        "player_id": 8473419,
        "shift_number": 1,
        "start_time": "00:17",
        "team_abbrev": "BOS",
        "team_id": 6,
        "team_name": "Boston Bruins",
        "type_code": 517,
        "game_type": 2,
    }
]

PLAYERS_DATA = [
    {
        "id": 8473419,
        "is_active": True,
        "current_team_id": 6,
        "current_team_abbrev": "BOS",
        "full_team_name": "Boston Bruins",
        "team_common_name": "Bruins",
        "team_place_name": "in Boston",
        "first_name": "Brad",
        "last_name": "Marchand",
        "team_logo": "https://assets.nhle.com/logos/nhl/svg/BOS_light.svg",
        "sweater_number": 63,
        "position": "L",
        "headshot": "https://assets.nhle.com/mugs/nhl/20232024/BOS/8473419.png",
        "hero_image": "https://assets.nhle.com/mugs/actionshots/1296x729/8473419.jpg",
        "height_in_inches": 69,
        "height_in_centimeters": 175,
        "weight_in_pounds": 181,
        "weight_in_kilograms": 82,
        "birth_date": "1988-05-11",
        "birth_city": "Halifax",
        "birth_state_province": "Nova Scotia",
        "birth_country": "CAN",
        "shoots_catches": "L",
        "draft_year": 2006,
        "draft_team_abbrev": "BOS",
        "draft_round": 3,
        "draft_pick_in_round": 21,
        "draft_overall_pick": 71,
    }
]

ROSTERS_DATA = [
    {"team_id": 6, "player_id": 8473419},
    {"team_id": 6, "player_id": 8476459},
    {"team_id": 8, "player_id": 8471214},
]


def _write(path: Path, filename: str, data) -> None:
    with open(path / filename, "w") as f:
        json.dump(data, f)


def _fetchone_as_dict(conn: sqlite3.Connection, sql: str) -> dict:
    conn.row_factory = sqlite3.Row
    row = conn.execute(sql).fetchone()
    return dict(row) if row else {}


class TestLoadToSqlite:
    @pytest.mark.unit
    def test_creates_teams_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            db_path = Path(tmp) / "out.db"
            _write(data_dir, "teams.json", TEAMS_DATA)

            load_to_sqlite(str(data_dir), str(db_path))

            conn = sqlite3.connect(str(db_path))
            row = _fetchone_as_dict(conn, "SELECT * FROM teams")
            conn.close()
            assert row == {
                "id": 6,
                "franchise_id": 6,
                "full_name": "Boston Bruins",
                "league_id": 133,
                "raw_tricode": "BOS",
                "tri_code": "BOS",
            }

    @pytest.mark.unit
    def test_creates_games_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            db_path = Path(tmp) / "out.db"
            _write(data_dir, "games.json", GAMES_DATA)

            load_to_sqlite(str(data_dir), str(db_path))

            conn = sqlite3.connect(str(db_path))
            row = _fetchone_as_dict(conn, "SELECT * FROM games")
            conn.close()
            assert row == {
                "id": 2023020001,
                "eastern_start_time": "19:00",
                "game_date": "2023-10-10",
                "game_number": 1,
                "game_schedule_state_id": 4,
                "game_state_id": 7,
                "game_type": 2,
                "home_score": 3,
                "home_team_id": 6,
                "period": None,
                "season": 20232024,
                "visiting_score": 2,
                "visiting_team_id": 8,
            }

    @pytest.mark.unit
    def test_creates_seasons_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            db_path = Path(tmp) / "out.db"
            _write(data_dir, "seasons.json", SEASONS_DATA)

            load_to_sqlite(str(data_dir), str(db_path))

            conn = sqlite3.connect(str(db_path))
            row = _fetchone_as_dict(conn, "SELECT * FROM seasons")
            conn.close()
            assert row == {
                "id": 20232024,
                "name": "20232024",
                "all_star_game_in_use": 0,
                "conferences_in_use": 1,
                "divisions_in_use": 1,
                "end_date": "2024-06-24",
                "entry_draft_in_use": 1,
                "formatted_season_id": "2023-24",
                "minimum_playoff_minutes_for_goalie_stats_leaders": 180,
                "minimum_regular_games_for_goalie_stats_leaders": 25,
                "nhl_stanley_cup_owner": 1,
                "number_of_games": 82,
                "olympics_participation": 0,
                "point_for_ot_loss_in_use": 1,
                "preseason_startdate": None,
                "regular_season_end_date": "2024-04-18",
                "row_in_use": 1,
                "season_ordinal": 107,
                "start_date": "2023-10-10",
                "supplemental_draft_in_use": 0,
                "ties_in_use": 0,
                "total_playoff_games": 89,
                "total_regular_season_games": 1312,
                "wildcard_in_use": 1,
            }

    @pytest.mark.unit
    def test_creates_game_results_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            db_path = Path(tmp) / "out.db"
            _write(data_dir, "pbp.json", PBP_DATA)

            load_to_sqlite(str(data_dir), str(db_path))

            conn = sqlite3.connect(str(db_path))
            row = _fetchone_as_dict(conn, "SELECT * FROM game_results")
            conn.close()
            assert row == {
                "id": 2023020001,
                "season": 20232024,
                "game_type": 2,
                "game_date": "2023-10-10",
                "venue": "TD Garden",
                "venue_location": "Boston, MA",
                "start_time_utc": "2023-10-10T23:00:00Z",
                "eastern_utc_offset": "-04:00",
                "venue_utc_offset": "-04:00",
                "game_state": "OFF",
                "game_schedule_state": "OK",
                "period": 3,
                "period_type": "REG",
                "away_team_id": 8,
                "away_team_name": "Canadiens",
                "away_team_abbreviation": "MTL",
                "away_team_logo": "https://assets.nhle.com/logos/nhl/svg/MTL_light.svg",
                "away_team_dark_logo": "https://assets.nhle.com/logos/nhl/svg/MTL_dark.svg",
                "home_team_id": 6,
                "home_team_name": "Bruins",
                "home_team_abbreviation": "BOS",
                "home_team_logo": "https://assets.nhle.com/logos/nhl/svg/BOS_light.svg",
                "home_team_dark_logo": "https://assets.nhle.com/logos/nhl/svg/BOS_dark.svg",
                "away_score": 1,
                "home_score": 3,
                "away_shots": 28,
                "home_shots": 35,
                "time_remaining": "00:00",
            }

    @pytest.mark.unit
    def test_creates_shifts_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            db_path = Path(tmp) / "out.db"
            _write(data_dir, "shifts.json", SHIFTS_DATA)

            load_to_sqlite(str(data_dir), str(db_path))

            conn = sqlite3.connect(str(db_path))
            row = _fetchone_as_dict(conn, "SELECT * FROM shifts")
            conn.close()
            assert row == {
                "id": 1,
                "detail_code": None,
                "duration": "00:45",
                "end_time": "01:02",
                "event_description": None,
                "event_details": None,
                "event_number": None,
                "first_name": "Brad",
                "game_id": 2023020001,
                "hex_value": "#FCB514",
                "last_name": "Marchand",
                "period": 1,
                "player_id": 8473419,
                "shift_number": 1,
                "start_time": "00:17",
                "team_abbrev": "BOS",
                "team_id": 6,
                "team_name": "Boston Bruins",
                "type_code": 517,
                "game_type": 2,
            }

    @pytest.mark.unit
    def test_creates_players_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            db_path = Path(tmp) / "out.db"
            _write(data_dir, "players.json", PLAYERS_DATA)

            load_to_sqlite(str(data_dir), str(db_path))

            conn = sqlite3.connect(str(db_path))
            row = _fetchone_as_dict(conn, "SELECT * FROM players")
            conn.close()
            assert row == {
                "id": 8473419,
                "is_active": 1,  # bool stored as INTEGER
                "current_team_id": 6,
                "current_team_abbrev": "BOS",
                "full_team_name": "Boston Bruins",
                "team_common_name": "Bruins",
                "team_place_name": "in Boston",
                "first_name": "Brad",
                "last_name": "Marchand",
                "team_logo": "https://assets.nhle.com/logos/nhl/svg/BOS_light.svg",
                "sweater_number": 63,
                "position": "L",
                "headshot": "https://assets.nhle.com/mugs/nhl/20232024/BOS/8473419.png",
                "hero_image": "https://assets.nhle.com/mugs/actionshots/1296x729/8473419.jpg",
                "height_in_inches": 69,
                "height_in_centimeters": 175,
                "weight_in_pounds": 181,
                "weight_in_kilograms": 82,
                "birth_date": "1988-05-11",
                "birth_city": "Halifax",
                "birth_state_province": "Nova Scotia",
                "birth_country": "CAN",
                "shoots_catches": "L",
                "draft_year": 2006,
                "draft_team_abbrev": "BOS",
                "draft_round": 3,
                "draft_pick_in_round": 21,
                "draft_overall_pick": 71,
            }

    @pytest.mark.unit
    def test_creates_rosters_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            db_path = Path(tmp) / "out.db"
            _write(data_dir, "rosters.json", ROSTERS_DATA)

            load_to_sqlite(str(data_dir), str(db_path))

            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            rows = [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM rosters ORDER BY team_id, player_id"
                ).fetchall()
            ]
            conn.close()
            assert rows == [
                {"team_id": 6, "player_id": 8473419},
                {"team_id": 6, "player_id": 8476459},
                {"team_id": 8, "player_id": 8471214},
            ]

    @pytest.mark.unit
    def test_creates_all_tables_even_when_files_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            db_path = Path(tmp) / "out.db"

            load_to_sqlite(str(data_dir), str(db_path))

            conn = sqlite3.connect(str(db_path))
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            assert tables == {
                "teams",
                "games",
                "seasons",
                "game_results",
                "shifts",
                "players",
                "rosters",
            }
            for table in tables:
                assert conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0
            conn.close()

    @pytest.mark.unit
    def test_empty_json_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            db_path = Path(tmp) / "out.db"
            _write(data_dir, "teams.json", [])

            load_to_sqlite(str(data_dir), str(db_path))

            conn = sqlite3.connect(str(db_path))
            assert conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0] == 0
            conn.close()


class TestToSqliteCommand:
    def setup_method(self):
        self.runner = CliRunner()

    @pytest.mark.integration
    def test_to_sqlite_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            db_path = Path(tmp) / "icetime.db"
            _write(data_dir, "teams.json", TEAMS_DATA)

            result = self.runner.invoke(
                app,
                ["to-sqlite", "--input-path", str(data_dir), "--output", str(db_path)],
            )

            assert result.exit_code == 0
            assert str(db_path) in result.stdout
            assert db_path.exists()

    @pytest.mark.integration
    def test_to_sqlite_quiet_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            db_path = Path(tmp) / "icetime.db"
            _write(data_dir, "teams.json", TEAMS_DATA)

            result = self.runner.invoke(
                app,
                [
                    "to-sqlite",
                    "--input-path",
                    str(data_dir),
                    "--output",
                    str(db_path),
                    "--quiet",
                ],
            )

            assert result.exit_code == 0
            assert result.stdout == ""

    @pytest.mark.unit
    def test_to_sqlite_error_handling(self):
        with patch("icetime.cli.load_to_sqlite", side_effect=Exception("disk full")):
            result = self.runner.invoke(
                app, ["to-sqlite", "--input-path", "/data", "--output", "/out.db"]
            )

        assert result.exit_code == 1
        assert "Error creating SQLite database: disk full" in result.stderr
