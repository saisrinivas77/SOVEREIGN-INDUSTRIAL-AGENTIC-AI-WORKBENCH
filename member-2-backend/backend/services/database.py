"""
Database persistence service using SQLite.
Stores task, file, document, artifact, and audit metadata.
"""

import json
import sqlite3
from typing import Any
from pathlib import Path
try:
    from backend.config import DATABASE_PATH
except (ImportError, ValueError):
    try:
        from ..config import DATABASE_PATH
    except (ImportError, ValueError):
        from config import DATABASE_PATH


class Database:
    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Files table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    file_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    mime_type TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    sha256 TEXT NOT NULL,
                    stored_path TEXT NOT NULL,
                    uploaded_at TEXT NOT NULL
                )
            """)

            # Tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    instruction TEXT NOT NULL,
                    file_ids TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    plan TEXT,
                    steps TEXT,
                    artifacts TEXT,
                    error TEXT
                )
            """)

            # Documents table (RAG indexing)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    file_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    indexed_at TEXT NOT NULL,
                    FOREIGN KEY(file_id) REFERENCES files(file_id)
                )
            """)

            # Audit events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    task_id TEXT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    component TEXT NOT NULL,
                    status TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
            """)

            # Security metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_metrics (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    network_mode TEXT NOT NULL DEFAULT 'restricted',
                    external_calls INTEGER NOT NULL DEFAULT 0,
                    external_ai_calls INTEGER NOT NULL DEFAULT 0,
                    blocked_attempts INTEGER NOT NULL DEFAULT 0,
                    local_calls INTEGER NOT NULL DEFAULT 0
                )
            """)

            # Initialize single row for security metrics if not present
            cursor.execute("""
                INSERT OR IGNORE INTO security_metrics (id, network_mode, external_calls, external_ai_calls, blocked_attempts, local_calls)
                VALUES (1, 'restricted', 0, 0, 0, 0)
            """)
            conn.commit()

    # --- File Operations ---
    def save_file(self, file_id: str, filename: str, mime_type: str, size: int, sha256: str, stored_path: str, uploaded_at: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO files (file_id, filename, mime_type, size, sha256, stored_path, uploaded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (file_id, filename, mime_type, size, sha256, stored_path, uploaded_at),
            )
            conn.commit()

    def get_file(self, file_id: str) -> dict[str, Any] | None:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM files WHERE file_id = ?", (file_id,)).fetchone()
            if row:
                return dict(row)
            return None

    def get_files_by_ids(self, file_ids: list[str]) -> list[dict[str, Any]]:
        if not file_ids:
            return []
        with self._get_connection() as conn:
            placeholders = ",".join("?" for _ in file_ids)
            rows = conn.execute(f"SELECT * FROM files WHERE file_id IN ({placeholders})", file_ids).fetchall()
            return [dict(row) for row in rows]

    # --- Task Operations ---
    def save_task(
        self,
        task_id: str,
        instruction: str,
        file_ids: list[str],
        task_type: str,
        status: str,
        created_at: str,
        updated_at: str,
        plan: dict[str, Any] | None = None,
        steps: list[dict[str, Any]] | None = None,
        artifacts: list[dict[str, Any]] | None = None,
        error: str | None = None,
    ) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO tasks (task_id, instruction, file_ids, task_type, status, created_at, updated_at, plan, steps, artifacts, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    instruction,
                    json.dumps(file_ids),
                    task_type,
                    status,
                    created_at,
                    updated_at,
                    json.dumps(plan) if plan is not None else None,
                    json.dumps(steps or []),
                    json.dumps(artifacts or []),
                    error,
                ),
            )
            conn.commit()

    def update_task(
        self,
        task_id: str,
        status: str | None = None,
        task_type: str | None = None,
        updated_at: str | None = None,
        plan: dict[str, Any] | None = None,
        steps: list[dict[str, Any]] | None = None,
        artifacts: list[dict[str, Any]] | None = None,
        error: str | None = None,
    ) -> None:
        updates = []
        params = []
        if status is not None:
            updates.append("status = ?")
            params.append(status)
        if task_type is not None:
            updates.append("task_type = ?")
            params.append(task_type)
        if updated_at is not None:
            updates.append("updated_at = ?")
            params.append(updated_at)
        if plan is not None:
            updates.append("plan = ?")
            params.append(json.dumps(plan))
        if steps is not None:
            updates.append("steps = ?")
            params.append(json.dumps(steps))
        if artifacts is not None:
            updates.append("artifacts = ?")
            params.append(json.dumps(artifacts))
        if error is not None:
            updates.append("error = ?")
            params.append(error)

        if not updates:
            return

        params.append(task_id)
        with self._get_connection() as conn:
            conn.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE task_id = ?", params)
            conn.commit()

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
            if not row:
                return None
            data = dict(row)
            data["file_ids"] = json.loads(data["file_ids"])
            data["plan"] = json.loads(data["plan"]) if data.get("plan") else None
            data["steps"] = json.loads(data["steps"]) if data.get("steps") else []
            data["artifacts"] = json.loads(data["artifacts"]) if data.get("artifacts") else []
            return data

    def list_all_tasks(self) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
            tasks = []
            for row in rows:
                data = dict(row)
                data["file_ids"] = json.loads(data["file_ids"])
                data["plan"] = json.loads(data["plan"]) if data.get("plan") else None
                data["steps"] = json.loads(data["steps"]) if data.get("steps") else []
                data["artifacts"] = json.loads(data["artifacts"]) if data.get("artifacts") else []
                tasks.append(data)
            return tasks

    def list_all_files(self) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM files ORDER BY uploaded_at DESC").fetchall()
            return [dict(row) for row in rows]

    # --- Document Operations (RAG) ---
    def save_document(self, document_id: str, file_id: str, status: str, indexed_at: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO documents (document_id, file_id, status, indexed_at)
                VALUES (?, ?, ?, ?)
                """,
                (document_id, file_id, status, indexed_at),
            )
            conn.commit()

    def get_document(self, document_id: str) -> dict[str, Any] | None:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM documents WHERE document_id = ?", (document_id,)).fetchone()
            if row:
                return dict(row)
            return None

    def list_all_documents(self) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT d.document_id, d.file_id, d.status as index_status, d.indexed_at,
                       f.filename, f.mime_type as type, f.size
                FROM documents d
                LEFT JOIN files f ON d.file_id = f.file_id
                ORDER BY d.indexed_at DESC
            """).fetchall()
            docs = []
            for r in rows:
                item = dict(r)
                item["processing_status"] = "COMPLETED"
                item["ocr_status"] = "COMPLETED"
                item["index_status"] = item.get("index_status", "INDEXED").upper()
                docs.append(item)
            return docs

    # --- Audit Operations ---
    def save_audit_event(
        self,
        event_id: str,
        task_id: str | None,
        timestamp: str,
        event_type: str,
        actor: str,
        component: str,
        status: str,
        metadata: dict[str, Any],
    ) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO audit_events (event_id, task_id, timestamp, event_type, actor, component, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (event_id, task_id, timestamp, event_type, actor, component, status, json.dumps(metadata)),
            )
            conn.commit()

    def get_audit_events_for_task(self, task_id: str) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM audit_events WHERE task_id = ? ORDER BY timestamp ASC",
                (task_id,),
            ).fetchall()
            events = []
            for row in rows:
                item = dict(row)
                item["metadata"] = json.loads(item["metadata"])
                events.append(item)
            return events

    def list_all_audit_events(self) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM audit_events ORDER BY timestamp DESC").fetchall()
            events = []
            for row in rows:
                item = dict(row)
                item["metadata"] = json.loads(item["metadata"])
                item["id"] = item["event_id"]
                item["type"] = item["event_type"].upper()
                item["description"] = f"Actor {item['actor']} invoked {item['component']} ({item['status']})"
                item["severity"] = "HIGH" if item["status"] == "failure" or item["type"] == "SECURITY" else "INFO"
                events.append(item)
            return events

    def list_recent_security_events(self, limit: int = 20) -> list[dict[str, Any]]:
        return self.list_all_audit_events()[:limit]

    def list_all_artifacts(self) -> list[dict[str, Any]]:

        tasks = self.list_all_tasks()
        all_artifacts = []
        for t in tasks:
            for a in t.get("artifacts", []):
                art_copy = dict(a)
                art_copy["task_id"] = t["task_id"]
                art_copy["created_at"] = t["updated_at"]
                all_artifacts.append(art_copy)
        return all_artifacts

    # --- Security Metrics Operations ---
    def get_security_metrics(self) -> dict[str, Any]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM security_metrics WHERE id = 1").fetchone()
            if row:
                return dict(row)
            return {
                "network_mode": "restricted",
                "external_calls": 0,
                "external_ai_calls": 0,
                "blocked_attempts": 0,
                "local_calls": 0,
            }

    def increment_security_metric(self, metric_name: str, count: int = 1) -> None:
        if metric_name not in ("external_calls", "external_ai_calls", "blocked_attempts", "local_calls"):
            return
        with self._get_connection() as conn:
            conn.execute(
                f"UPDATE security_metrics SET {metric_name} = {metric_name} + ? WHERE id = 1",
                (count,),
            )
            conn.commit()


# Singleton database instance
db = Database()

