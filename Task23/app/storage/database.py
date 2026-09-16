import sqlite3
from pathlib import Path
from app.config import settings

def get_connection():
    path = Path(settings.database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS evaluation_runs (
            run_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, suite TEXT, model TEXT,
            prompt_version TEXT, report_json TEXT NOT NULL)""")
        conn.commit()
