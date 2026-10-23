import json
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

from research_agent.config import settings
from research_agent.models import HistoryItem, ResearchResponse


def _connect() -> sqlite3.Connection:
    path = Path(settings.database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with closing(_connect()) as connection, connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS research_runs (
                run_id TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                report TEXT NOT NULL,
                sources_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )"""
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_research_runs_created_at "
            "ON research_runs(created_at DESC)"
        )


def save_run(result: ResearchResponse) -> None:
    with closing(_connect()) as connection, connection:
        connection.execute(
            "INSERT INTO research_runs(run_id, query, report, sources_json, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                result.run_id,
                result.query,
                result.report,
                json.dumps([source.model_dump(mode="json") for source in result.sources]),
                result.created_at.astimezone(UTC).isoformat(),
            ),
        )


def get_run(run_id: str) -> ResearchResponse | None:
    with closing(_connect()) as connection, connection:
        row = connection.execute(
            "SELECT * FROM research_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
    if row is None:
        return None
    return ResearchResponse(
        run_id=row["run_id"],
        query=row["query"],
        report=row["report"],
        sources=json.loads(row["sources_json"]),
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def list_runs(limit: int = 20) -> list[HistoryItem]:
    with closing(_connect()) as connection, connection:
        rows = connection.execute(
            "SELECT run_id, query, created_at, sources_json FROM research_runs "
            "ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [
        HistoryItem(
            run_id=row["run_id"],
            query=row["query"],
            created_at=datetime.fromisoformat(row["created_at"]),
            source_count=len(json.loads(row["sources_json"])),
        )
        for row in rows
    ]
