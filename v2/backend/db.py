import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

DB_FILE = Path(__file__).resolve().parent / "workflow_history.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS executions (
    id TEXT PRIMARY KEY,
    workflow_id TEXT,
    name TEXT,
    task_id TEXT,
    status TEXT,
    results TEXT,
    started_at TEXT,
    finished_at TEXT
);
CREATE TABLE IF NOT EXISTS workflows (
    id TEXT PRIMARY KEY,
    name TEXT,
    workflow_json TEXT,
    updated_at TEXT
);
"""


def init_db() -> None:
    conn = sqlite3.connect(DB_FILE)
    with conn:
        conn.executescript(CREATE_TABLE_SQL)
    conn.close()


def save_execution_history(
    task_id: str,
    workflow_id: str,
    name: str,
    status: str,
    results: Dict[str, Any],
    started_at: str,
    finished_at: str,
) -> None:
    conn = sqlite3.connect(DB_FILE)
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO executions (id, workflow_id, name, task_id, status, results, started_at, finished_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                task_id,
                workflow_id,
                name,
                task_id,
                status,
                json.dumps(results),
                started_at,
                finished_at,
            ),
        )
    conn.close()


def get_execution_history() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, workflow_id, name, task_id, status, results, started_at, finished_at FROM executions ORDER BY started_at DESC")
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "workflow_id": row[1],
            "name": row[2],
            "task_id": row[3],
            "status": row[4],
            "results": json.loads(row[5]) if row[5] else {},
            "started_at": row[6],
            "finished_at": row[7],
        }
        for row in rows
    ]


def save_workflow(workflow_id: str, name: str, workflow_json: dict) -> None:
    conn = sqlite3.connect(DB_FILE)
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO workflows (id, name, workflow_json, updated_at) VALUES (?, ?, ?, ?)",
            (
                workflow_id,
                name,
                json.dumps(workflow_json),
                datetime.now().isoformat(),
            ),
        )
    conn.close()
