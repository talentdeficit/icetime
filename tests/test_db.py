import json
import sqlite3
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from icetime.cli import app
from icetime.db import load_to_sqlite


TEAMS_DATA = [
    {
        "id": 1,
        "franchise_id": 1,
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
        "home_team_id": 1,
        "period": None,
        "season": 20232024,
        "visiting_score": 2,
        "visiting_team_id": 2,
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

ROSTERS_DATA = [
    {"team_id": 1, "player_id": 8478402},
    {"team_id": 1, "player_id": 8476459},
    {"team_id": 2, "player_id": 8471214},
]


def _write(path: Path, filename: str, data) -> None:
    with open(path / filename, "w") as f:
        json.dump(data, f)


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
            rows = conn.execute("SELECT id, full_name, tri_code FROM teams").fetchall()
            conn.close()
            assert len(rows) == 1
            assert rows[0] == (1, "Boston Bruins", "BOS")

    @pytest.mark.unit
    def test_creates_games_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            db_path = Path(tmp) / "out.db"
            _write(data_dir, "games.json", GAMES_DATA)

            load_to_sqlite(str(data_dir), str(db_path))

            conn = sqlite3.connect(str(db_path))
            rows = conn.execute("SELECT id, season, game_type FROM games").fetchall()
            conn.close()
            assert rows == [(2023020001, 20232024, 2)]

    @pytest.mark.unit
    def test_creates_seasons_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            db_path = Path(tmp) / "out.db"
            _write(data_dir, "seasons.json", SEASONS_DATA)

            load_to_sqlite(str(data_dir), str(db_path))

            conn = sqlite3.connect(str(db_path))
            rows = conn.execute("SELECT id, name FROM seasons").fetchall()
            conn.close()
            assert rows == [(20232024, "20232024")]

    @pytest.mark.unit
    def test_creates_rosters_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            db_path = Path(tmp) / "out.db"
            _write(data_dir, "rosters.json", ROSTERS_DATA)

            load_to_sqlite(str(data_dir), str(db_path))

            conn = sqlite3.connect(str(db_path))
            rows = conn.execute(
                "SELECT team_id, player_id FROM rosters ORDER BY player_id"
            ).fetchall()
            conn.close()
            assert len(rows) == 3
            assert (1, 8476459) in rows
            assert (2, 8471214) in rows

    @pytest.mark.unit
    def test_creates_all_tables_even_when_files_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            db_path = Path(tmp) / "out.db"
            _write(data_dir, "teams.json", TEAMS_DATA)

            load_to_sqlite(str(data_dir), str(db_path))

            conn = sqlite3.connect(str(db_path))
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            # All tables created regardless of which files are present
            assert {
                "teams",
                "games",
                "seasons",
                "game_results",
                "shifts",
                "players",
                "rosters",
            } <= tables
            # Tables with no file have no rows
            assert conn.execute("SELECT COUNT(*) FROM games").fetchone()[0] == 0
            assert conn.execute("SELECT COUNT(*) FROM rosters").fetchone()[0] == 0
            # Table with file has rows
            assert conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0] == 1
            conn.close()

    @pytest.mark.unit
    def test_multiple_tables_in_one_db(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            db_path = Path(tmp) / "out.db"
            _write(data_dir, "teams.json", TEAMS_DATA)
            _write(data_dir, "games.json", GAMES_DATA)
            _write(data_dir, "rosters.json", ROSTERS_DATA)

            load_to_sqlite(str(data_dir), str(db_path))

            conn = sqlite3.connect(str(db_path))
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            conn.close()
            assert {"teams", "games", "rosters"} <= tables

    @pytest.mark.unit
    def test_empty_json_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            db_path = Path(tmp) / "out.db"
            _write(data_dir, "teams.json", [])

            load_to_sqlite(str(data_dir), str(db_path))

            conn = sqlite3.connect(str(db_path))
            rows = conn.execute("SELECT * FROM teams").fetchall()
            conn.close()
            assert rows == []


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
                [
                    "to-sqlite",
                    "--input-path",
                    str(data_dir),
                    "--output",
                    str(db_path),
                ],
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
        from unittest.mock import patch

        with patch("icetime.cli.load_to_sqlite", side_effect=Exception("disk full")):
            result = self.runner.invoke(
                app, ["to-sqlite", "--input-path", "/data", "--output", "/out.db"]
            )

        assert result.exit_code == 1
        assert "Error creating SQLite database: disk full" in result.stderr
