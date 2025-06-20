import json
import requests
import typer
from pathlib import Path
from icetime.report import reporter
from icetime import __app_name__, __version__

app = typer.Typer()


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
    url = "https://api.nhle.com/stats/rest/en/team"

    with reporter(quiet) as progress:
        try:
            task = progress.add_task(description="Processing get-teams", total=None)

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            progress.update(task, total=data.get("total", 0))

            # Sort the data array by id field
            if "data" in data and isinstance(data["data"], list):
                data["data"] = sorted(data["data"], key=lambda x: x.get("id", 0))

            # Create output directory if it doesn't exist
            Path(output_path).mkdir(parents=True, exist_ok=True)

            # Write to file
            output_file = Path(output_path) / "teams.json"
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)

            progress.update(task, completed=data.get("total", 0))

        except requests.exceptions.RequestException as e:
            typer.echo(f"Error fetching teams: {e}", err=True)
            raise typer.Exit(1)


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
    url = "https://api.nhle.com/stats/rest/en/game"

    with reporter(quiet) as progress:
        try:
            task = progress.add_task(description="Processing get-games", total=None)

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            progress.update(task, total=data.get("total", 0))

            # Sort the data array by id field
            if "data" in data and isinstance(data["data"], list):
                data["data"] = sorted(data["data"], key=lambda x: x.get("id", 0))

            # Create output directory if it doesn't exist
            Path(output_path).mkdir(parents=True, exist_ok=True)

            # Write to file
            output_file = Path(output_path) / "games.json"
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)

            progress.update(task, completed=data.get("total", 0))

        except requests.exceptions.RequestException as e:
            typer.echo(f"Error fetching games: {e}", err=True)
            raise typer.Exit(1)


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
    url = "https://api.nhle.com/stats/rest/en/season"

    with reporter(quiet) as progress:
        try:
            task = progress.add_task(description="Processing get-seasons", total=None)

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            progress.update(task, total=data.get("total", 0))

            # Sort the data array by id field
            if "data" in data and isinstance(data["data"], list):
                data["data"] = sorted(data["data"], key=lambda x: x.get("id", 0))

            # Create output directory if it doesn't exist
            Path(output_path).mkdir(parents=True, exist_ok=True)

            # Write to file
            output_file = Path(output_path) / "season.json"
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)

            progress.update(task, completed=data.get("total", 0))
        except requests.exceptions.RequestException as e:
            typer.echo(f"Error fetching season: {e}", err=True)
            raise typer.Exit(1)


@app.command()
def get_pbp(
    season: str = typer.Option(..., "--season", help="Season to filter games by"),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Disable all stdout output"
    ),
    output_path: str = typer.Option(
        "./data", "--output-path", help="Directory to save output files"
    ),
) -> None:
    """Get play-by-play data for games in a specific season."""
    games_url = "https://api.nhle.com/stats/rest/en/game"

    with reporter(quiet) as progress:
        try:
            task = progress.add_task(description="Processing get-pbp", total=None)

            response = requests.get(games_url)
            response.raise_for_status()
            games_data = response.json()

            # Filter games by season
            filtered_games = []
            if "data" in games_data and isinstance(games_data["data"], list):
                filtered_games = [
                    game
                    for game in games_data["data"]
                    if str(game.get("season", "")) == season
                ]

            progress.update(task, total=len(filtered_games))

            if not filtered_games:
                return

            # Get play-by-play data for each filtered game
            pbp_data = []
            for i, game in enumerate(filtered_games):
                game_id = game.get("id")
                if game_id:
                    pbp_url = (
                        f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
                    )

                    try:
                        pbp_response = requests.get(pbp_url)
                        pbp_response.raise_for_status()
                        pbp_result = pbp_response.json()
                        pbp_data.append(pbp_result)

                    except requests.exceptions.RequestException as e:
                        if e.response and e.response.status_code == 404:
                            pass
                        else:
                            typer.echo(
                                f"Error fetching play-by-play for game {game_id}: {e}",
                                err=True,
                            )
                            raise typer.Exit(1)

                    progress.update(task, advance=1)

            # Create final JSON structure
            result = {"data": pbp_data, "total": len(pbp_data)}

            # Create output directory if it doesn't exist
            Path(output_path).mkdir(parents=True, exist_ok=True)

            # Write to file
            output_file = Path(output_path) / "pbp.json"
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)

        except requests.exceptions.RequestException as e:
            typer.echo(f"Error fetching games: {e}", err=True)
            raise typer.Exit(1)


@app.command()
def get_shifts(
    season: str = typer.Option(..., "--season", help="Season to filter games by"),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Disable all stdout output"
    ),
    output_path: str = typer.Option(
        "./data", "--output-path", help="Directory to save output files"
    ),
) -> None:
    """Get shift chart data for games in a specific season."""
    games_url = "https://api.nhle.com/stats/rest/en/game"

    with reporter(quiet) as progress:
        try:
            task = progress.add_task(description="Processing get-shifts", total=None)

            response = requests.get(games_url)
            response.raise_for_status()
            games_data = response.json()

            # Filter games by season
            filtered_games = []
            if "data" in games_data and isinstance(games_data["data"], list):
                filtered_games = [
                    game
                    for game in games_data["data"]
                    if str(game.get("season", "")) == season
                ]

            progress.update(task, total=len(filtered_games))

            # Get shift chart data for each filtered game
            shifts_data = []
            for i, game in enumerate(filtered_games):
                game_id = game.get("id")
                if game_id:
                    shifts_url = f"https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId={game_id}"

                    try:
                        shifts_response = requests.get(shifts_url)
                        shifts_response.raise_for_status()
                        shifts_result = shifts_response.json()
                        shifts_data.append(shifts_result)

                    except requests.exceptions.RequestException as e:
                        if e.response and e.response.status_code == 404:
                            pass
                        else:
                            typer.echo(
                                f"Error fetching play-by-play for game {game_id}: {e}",
                                err=True,
                            )
                            raise typer.Exit(1)

                    progress.update(task, advance=1)

            # Create final JSON structure
            result = {"data": shifts_data, "total": len(shifts_data)}

            # Create output directory if it doesn't exist
            Path(output_path).mkdir(parents=True, exist_ok=True)

            # Write to file
            output_file = Path(output_path) / "shifts.json"
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)

        except requests.exceptions.RequestException:
            raise typer.Exit(1)


@app.command()
def get_all(
    season: str = typer.Option(..., "--season", help="Season to filter games by"),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Disable all stdout output"
    ),
    output_path: str = typer.Option(
        "./data", "--output-path", help="Directory to save output files"
    ),
) -> None:
    """Get all NHL teams, games, and season data."""
    get_teams(quiet, output_path)
    get_games(quiet, output_path)
    get_seasons(quiet, output_path)
    get_pbp(season, quiet, output_path)
    get_shifts(season, quiet, output_path)


@app.command()
def version() -> None:
    """Show version information."""
    typer.echo(f"{__app_name__} v{__version__}")
