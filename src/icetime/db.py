import json
import sqlite3
import types as _types
from pathlib import Path
from typing import Union, get_args, get_origin

from icetime.models import Game, GameResult, Player, Season, Shift, Team


def _annotation_to_sqlite(annotation) -> str:
    origin = get_origin(annotation)
    if origin is Union or isinstance(annotation, _types.UnionType):
        non_none = [a for a in get_args(annotation) if a is not type(None)]
        if len(non_none) == 1:
            return _annotation_to_sqlite(non_none[0])
    if annotation is bool:
        return "INTEGER"
    if annotation is int:
        return "INTEGER"
    if annotation is float:
        return "REAL"
    return "TEXT"


def _model_schema(model_class) -> list[tuple[str, str, bool]]:
    return [
        (name, _annotation_to_sqlite(field.annotation), name == "id")
        for name, field in model_class.model_fields.items()
    ]


def _create_table(conn: sqlite3.Connection, table: str, schema: list) -> None:
    cols = []
    for name, sqlite_type, is_pk in schema:
        col = f"{name} {sqlite_type}"
        if is_pk:
            col += " PRIMARY KEY"
        cols.append(col)
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(cols)})")


def _insert_records(
    conn: sqlite3.Connection, table: str, schema: list, records: list[dict]
) -> None:
    if not records:
        return
    cols = [name for name, _, _ in schema]
    placeholders = ", ".join("?" * len(cols))
    sql = f"INSERT OR REPLACE INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
    conn.executemany(sql, [tuple(r.get(col) for col in cols) for r in records])


_MODEL_FILES: list[tuple[str, type, str]] = [
    ("teams", Team, "teams.json"),
    ("games", Game, "games.json"),
    ("seasons", Season, "seasons.json"),
    ("game_results", GameResult, "pbp.json"),
    ("shifts", Shift, "shifts.json"),
    ("players", Player, "players.json"),
]


def load_to_sqlite(input_path: str, output: str) -> None:
    conn = sqlite3.connect(output)
    try:
        for table, model_class, filename in _MODEL_FILES:
            schema = _model_schema(model_class)
            _create_table(conn, table, schema)
            filepath = Path(input_path) / filename
            if filepath.exists():
                with open(filepath) as f:
                    records = json.load(f)
                _insert_records(conn, table, schema, records)

        conn.execute(
            "CREATE TABLE IF NOT EXISTS rosters "
            "(team_id INTEGER NOT NULL, player_id INTEGER NOT NULL, "
            "PRIMARY KEY (team_id, player_id))"
        )
        rosters_path = Path(input_path) / "rosters.json"
        if rosters_path.exists():
            with open(rosters_path) as f:
                rosters = json.load(f)
            conn.executemany(
                "INSERT OR REPLACE INTO rosters (team_id, player_id) VALUES (?, ?)",
                [(r["team_id"], r["player_id"]) for r in rosters],
            )

        conn.commit()
    finally:
        conn.close()
