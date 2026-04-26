import typer
from pathlib import Path
from icetime.api import StatsApi, NotFoundError
from icetime.db import load_to_sqlite
from icetime.report import reporter
from icetime import __app_name__, __version__
from pydantic import TypeAdapter
from typing import List, Dict
from icetime.models import Team, Game, Season, GameResult, Shift

app = typer.Typer()
api = StatsApi()


def _save_list(
    quiet, output_path, task_name, fetch_fn, filename, model_type, error_label
):
    with reporter(quiet) as progress:
        try:
            task = progress.add_task(description=f"Processing {task_name}", total=None)
            items = fetch_fn()
            progress.update(task, total=len(items))
            Path(output_path).mkdir(parents=True, exist_ok=True)
            with open(Path(output_path) / filename, "wb") as f:
                f.write(TypeAdapter(List[model_type]).dump_json(items, indent=2))
            progress.update(task, completed=len(items))
        except Exception as e:
            typer.echo(f"Error fetching {error_label}: {e}", err=True)
            raise typer.Exit(1)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command()
def get_teams(
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Disable all stdout output"
    ),
    output_path: str = typer.Option(
        "./data", "--output-path", help="Directory to save output files"
    ),
) -> None:
    """List all NHL teams."""
    _save_list(
        quiet, output_path, "get-teams", api.get_teams, "teams.json", Team, "teams"
    )


@app.command()
def get_games(
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Disable all stdout output"
    ),
    output_path: str = typer.Option(
        "./data", "--output-path", help="Directory to save output files"
    ),
) -> None:
    """List all NHL games."""
    _save_list(
        quiet, output_path, "get-games", api.get_games, "games.json", Game, "games"
    )


@app.command()
def get_seasons(
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Disable all stdout output"
    ),
    output_path: str = typer.Option(
        "./data", "--output-path", help="Directory to save output files"
    ),
) -> None:
    """List all NHL seasons."""
    _save_list(
        quiet,
        output_path,
        "get-seasons",
        api.get_seasons,
        "seasons.json",
        Season,
        "seasons",
    )


@app.command()
def get_pbp(
    season: int = typer.Option(..., "--season", help="Season to filter games by"),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Disable all stdout output"
    ),
    output_path: str = typer.Option(
        "./data", "--output-path", help="Directory to save output files"
    ),
) -> None:
    """Get play-by-play data for games in a specific season."""
    with reporter(quiet) as progress:
        try:
            task = progress.add_task(description="Processing get-pbp", total=None)

            filtered_games = api.get_games_by_season(season)
            progress.update(task, total=len(filtered_games))

            if not filtered_games:
                return

            # Get play-by-play data for each filtered game
            pbp_data = []
            for game in filtered_games:
                if game.id:
                    try:
                        pbp_result = api.get_play_by_play(game)
                        if pbp_result:
                            pbp_data.append(pbp_result)
                    except NotFoundError:
                        pass
                    except Exception as e:
                        typer.echo(
                            f"Error fetching play-by-play for game {game.id}: {e}",
                            err=True,
                        )
                        raise typer.Exit(1)

                    progress.update(task, advance=1)

            # Create output directory if it doesn't exist
            Path(output_path).mkdir(parents=True, exist_ok=True)

            # Write to file
            output_file = Path(output_path) / "pbp.json"
            with open(output_file, "wb") as f:
                games_adapter = TypeAdapter(List[GameResult])
                games_json_bytes = games_adapter.dump_json(pbp_data, indent=2)
                f.write(games_json_bytes)

        except Exception as e:
            typer.echo(f"Error fetching play-by-play: {e}", err=True)
            raise typer.Exit(1)


@app.command()
def get_shifts(
    season: int = typer.Option(..., "--season", help="Season to filter games by"),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Disable all stdout output"
    ),
    output_path: str = typer.Option(
        "./data", "--output-path", help="Directory to save output files"
    ),
) -> None:
    """Get shift chart data for games in a specific season."""
    with reporter(quiet) as progress:
        try:
            task = progress.add_task(description="Processing get-shifts", total=None)

            filtered_games = api.get_games_by_season(season)
            progress.update(task, total=len(filtered_games))

            # Get shift chart data for each filtered game
            shifts_data = []
            for game in filtered_games:
                if game.id:
                    try:
                        shifts_result = api.get_shift_charts(game)
                        if shifts_result:
                            shifts_data.extend(shifts_result)
                    except NotFoundError:
                        pass
                    except Exception as e:
                        typer.echo(
                            f"Error fetching shift charts for game {game.id}: {e}",
                            err=True,
                        )
                        raise typer.Exit(1)

                    progress.update(task, advance=1)

            # Create output directory if it doesn't exist
            Path(output_path).mkdir(parents=True, exist_ok=True)

            # Write to file
            output_file = Path(output_path) / "shifts.json"
            with open(output_file, "wb") as f:
                shifts_adapter = TypeAdapter(List[Shift])
                shifts_json_bytes = shifts_adapter.dump_json(shifts_data, indent=2)
                f.write(shifts_json_bytes)

        except Exception as e:
            typer.echo(f"Error fetching shifts: {e}", err=True)
            raise typer.Exit(1)


@app.command()
def get_rosters(
    season: int = typer.Option(..., "--season", help="Season to get rosters for"),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Disable all stdout output"
    ),
    output_path: str = typer.Option(
        "./data", "--output-path", help="Directory to save output files"
    ),
) -> None:
    """Get team rosters for all teams in a specific season."""
    with reporter(quiet) as progress:
        try:
            task = progress.add_task(description="Processing get-rosters", total=None)
            teams = api.get_teams()
            progress.update(task, total=len(teams))

            roster_entries = []

            for team in teams:
                if team.tri_code:
                    try:
                        roster = api.get_roster_by_season(team.tri_code, season)
                        if roster:
                            # Create entries for each player
                            for player_id in roster.all_player_ids:
                                roster_entries.append(
                                    {"team_id": team.id, "player_id": player_id}
                                )
                    except NotFoundError:
                        pass
                    except Exception as e:
                        typer.echo(
                            f"Error fetching roster for team {team.tri_code}: {e}",
                            err=True,
                        )
                        raise typer.Exit(1)
                    progress.update(task, advance=1)

            # Create output directory if it doesn't exist
            Path(output_path).mkdir(parents=True, exist_ok=True)

            # Write to file
            output_file = Path(output_path) / "rosters.json"
            with open(output_file, "wb") as f:
                rosters_adapter = TypeAdapter(List[Dict[str, object]])
                rosters_json_bytes = rosters_adapter.dump_json(roster_entries, indent=2)
                f.write(rosters_json_bytes)

        except Exception as e:
            typer.echo(f"Error fetching rosters: {e}", err=True)
            raise typer.Exit(1)


@app.command()
def get_all(
    season: int = typer.Option(..., "--season", help="Season to filter games by"),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Disable all stdout output"
    ),
    output_path: str = typer.Option(
        "./data", "--output-path", help="Directory to save output files"
    ),
) -> None:
    """Get all NHL data for a season."""
    get_teams(quiet, output_path)
    get_games(quiet, output_path)
    get_seasons(quiet, output_path)
    get_pbp(season, quiet, output_path)
    get_shifts(season, quiet, output_path)
    get_rosters(season, quiet, output_path)


@app.command()
def to_sqlite(
    input_path: str = typer.Option(
        "./data", "--input-path", help="Directory with JSON data files"
    ),
    output: str = typer.Option(
        "./icetime.db", "--output", help="SQLite output file path"
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Disable all stdout output"
    ),
) -> None:
    """Convert JSON data files to a SQLite database."""
    try:
        load_to_sqlite(input_path, output)
        if not quiet:
            typer.echo(f"SQLite database written to {output}")
    except Exception as e:
        typer.echo(f"Error creating SQLite database: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    typer.echo(f"{__app_name__} v{__version__}")
