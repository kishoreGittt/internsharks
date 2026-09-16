import json
import uuid
from datetime import datetime, timezone
from app.storage.database import get_connection

def save_run(report: dict) -> str:
    run_id = "eval_run_" + uuid.uuid4().hex[:12]
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO evaluation_runs VALUES (?, ?, ?, ?, ?, ?)",
            (run_id, datetime.now(timezone.utc).isoformat(), report["suite"], report["model"], report["prompt_version"], json.dumps(report))
        )
        conn.commit()
    return run_id

def get_run(run_id: str):
    with get_connection() as conn:
        row = conn.execute("SELECT report_json FROM evaluation_runs WHERE run_id = ?", (run_id,)).fetchone()
    return json.loads(row["report_json"]) if row else None
