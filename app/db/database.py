import sqlite3
from pathlib import Path
from typing import List

DB_PATH = Path(__file__).resolve().parents[2] / "specimen_records.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                image_path TEXT NOT NULL,
                specimen_size_mm REAL NOT NULL,
                microscope_type TEXT NOT NULL,
                output_unit TEXT NOT NULL,
                actual_size_mm REAL NOT NULL,
                actual_size_output REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()


def list_records() -> List[sqlite3.Row]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, username, image_path, specimen_size_mm, microscope_type,
                   output_unit, actual_size_mm, actual_size_output, created_at
            FROM calculations
            ORDER BY id DESC
            """
        ).fetchall()
    return rows


def insert_record(
    username: str,
    image_path: str,
    specimen_size_mm: float,
    microscope_type: str,
    output_unit: str,
    actual_size_mm: float,
    actual_size_output: float,
) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO calculations (
                username, image_path, specimen_size_mm, microscope_type,
                output_unit, actual_size_mm, actual_size_output
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                image_path,
                specimen_size_mm,
                microscope_type,
                output_unit,
                actual_size_mm,
                actual_size_output,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def delete_record(record_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM calculations WHERE id = ?", (record_id,))
        conn.commit()


def clear_records() -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM calculations")
        conn.commit()
