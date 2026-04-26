# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`icetime` is a Python CLI tool for fetching, processing, and persisting NHL statistics from the NHL API. It uses the Typer framework for command-line interface and fetches data from multiple NHL API endpoints.

## Architecture

The application is structured as a single-module CLI with these key components:

- **Entry Point**: `src/icetime/__main__.py` - provides the main entry point
- **CLI Commands**: `src/icetime/cli.py` - contains all command definitions using Typer
- **Data Storage**: `data/` directory - JSON files for teams, games, seasons, play-by-play, and shifts
- **API Documentation**: `misc/nhl-api-docs.md` - comprehensive reference for NHL API endpoints

### Core Commands

- `get-teams` - Fetches all NHL team data
- `get-games` - Fetches all NHL game data  
- `get-seasons` - Fetches all NHL season data
- `get-pbp --season <YYYYYYY>` - Fetches play-by-play data for specific season
- `get-shifts --season <YYYYYYY>` - Fetches shift chart data for specific season
- `get-all --season <YYYYYYY>` - Runs all commands for a season
- `version` - Shows version information

## Development Commands

### Tests, Linting, and Formatting

After every code change, run `make ci` and fix any errors before considering the task complete.

### Running the CLI
```bash
# Install in development mode
uv pip install -e .

# Run commands
uv run src/icetime --help
uv run src/icetime get-teams
uv run src/icetime get-all --season 20232024
```

### Package Management
This project uses `uv` for dependency management:
```bash
# Install dependencies
uv pip install -r requirements.txt

# Add new dependency
uv add package-name
```

## API Integration

The tool integrates with two primary NHL APIs:

1. **Stats API** (`api.nhle.com/stats/rest`) - Used for teams, games, seasons, shifts
2. **Web API** (`api-web.nhle.com`) - Used for play-by-play data

Season format: `YYYYYYY` (e.g., `20232024` for 2023-2024 season)

## Data Output

All commands save JSON data to the `data/` directory by default (configurable via `--output-path`):
- `teams.json` - Team information
- `games.json` - Game information  
- `season.json` - Season information
- `pbp.json` - Play-by-play data
- `shifts.json` - Shift chart data

Data is automatically sorted by ID and includes progress indicators during fetching.

## Dependencies

- `typer` - CLI framework
- `requests` - HTTP client for API calls
- `rich` - Progress indicators and formatted output