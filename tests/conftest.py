import pytest
import tempfile
from pathlib import Path
import json


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_team_data():
    """Sample team data for testing."""
    current_file_directory = Path(__file__).parent.resolve()
    with open(current_file_directory / "fixtures/teams.json", "r") as f:
        teams = json.load(f)
        return teams


@pytest.fixture
def sample_game_data():
    """Sample game data for testing."""
    current_file_directory = Path(__file__).parent.resolve()
    with open(current_file_directory / "fixtures/games.json", "r") as f:
        games = json.load(f)
        return games


@pytest.fixture
def sample_season_data():
    """Sample season data for testing."""
    current_file_directory = Path(__file__).parent.resolve()
    with open(current_file_directory / "fixtures/seasons.json", "r") as f:
        seasons = json.load(f)
        return seasons


@pytest.fixture
def sample_pbp_data():
    """Sample play-by-play data for testing."""
    current_file_directory = Path(__file__).parent.resolve()
    with open(current_file_directory / "fixtures/pbp.json", "r") as f:
        pbp = json.load(f)
        return pbp


@pytest.fixture
def sample_shifts_data():
    """Sample shifts data for testing Shift and Shifts models."""
    current_file_directory = Path(__file__).parent.resolve()
    with open(current_file_directory / "fixtures/shifts.json", "r") as f:
        shifts = json.load(f)
        return shifts
