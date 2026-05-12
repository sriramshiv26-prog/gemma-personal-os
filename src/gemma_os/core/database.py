"""
Database module - Task history, results, and audit logging
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from .config import Config


class Database:
    """SQLite database for task persistence and audit logging"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.db_path = Path.home() / ".gemma-os" / "gemma_os.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def init(self):
        """Initialize database schema"""
        conn = self.connect()
        cursor = conn.cursor()

        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                task_name TEXT NOT NULL,
                task_type TEXT,
                status TEXT NOT NULL,
                input_data TEXT,
                output_data TEXT,
                model_selected TEXT,
                routing_reason TEXT,
                skill_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                execution_time_ms INTEGER,
                tokens_input INTEGER,
                tokens_output INTEGER
            )
        """)

        # Indexes for tasks table
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at)")

        # Audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                severity TEXT DEFAULT 'INFO',
                FOREIGN KEY (task_id) REFERENCES tasks(task_id)
            )
        """)

        # Indexes for audit_log table
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_task_id ON audit_log(task_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)")

        # API calls table (for external service tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                api_name TEXT NOT NULL,
                method TEXT,
                endpoint TEXT,
                request_data TEXT,
                response_status INTEGER,
                response_time_ms INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(task_id)
            )
        """)

        # Indexes for api_calls table
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_calls_task_id ON api_calls(task_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_calls_api_name ON api_calls(api_name)")

        conn.commit()
        conn.close()

    def create_task(
        self,
        task_id: str,
        task_name: str,
        task_type: str = "general",
        input_data: Dict[str, Any] = None,
    ) -> int:
        """Create a new task entry"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tasks (task_id, task_name, task_type, status, input_data)
            VALUES (?, ?, ?, ?, ?)
        """, (
            task_id,
            task_name,
            task_type,
            "started",
            json.dumps(input_data or {}),
        ))

        conn.commit()
        conn.close()
        return cursor.lastrowid

    def update_task(
        self,
        task_id: str,
        status: str,
        output_data: Dict[str, Any] = None,
        execution_time_ms: int = None,
        tokens_input: int = None,
        tokens_output: int = None,
        model_selected: str = None,
        routing_reason: str = None,
        skill_used: str = None,
    ):
        """Update task status and results"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE tasks
            SET status = ?,
                output_data = ?,
                execution_time_ms = ?,
                tokens_input = ?,
                tokens_output = ?,
                model_selected = ?,
                routing_reason = ?,
                skill_used = ?,
                completed_at = CASE WHEN ? = 'completed' THEN CURRENT_TIMESTAMP ELSE completed_at END
            WHERE task_id = ?
        """, (
            status,
            json.dumps(output_data or {}),
            execution_time_ms,
            tokens_input,
            tokens_output,
            model_selected,
            routing_reason,
            skill_used,
            status,
            task_id,
        ))

        conn.commit()
        conn.close()

    def log_audit(
        self,
        task_id: str,
        event_type: str,
        event_data: Dict[str, Any] = None,
        severity: str = "INFO",
    ):
        """Log audit event"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO audit_log (task_id, event_type, event_data, severity)
            VALUES (?, ?, ?, ?)
        """, (
            task_id,
            event_type,
            json.dumps(event_data or {}),
            severity,
        ))

        conn.commit()
        conn.close()

    def log_api_call(
        self,
        task_id: str,
        api_name: str,
        method: str,
        endpoint: str,
        response_status: int,
        response_time_ms: int,
        request_data: Dict[str, Any] = None,
    ):
        """Log external API call"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO api_calls
            (task_id, api_name, method, endpoint, request_data, response_status, response_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id,
            api_name,
            method,
            endpoint,
            json.dumps(request_data or {}),
            response_status,
            response_time_ms,
        ))

        conn.commit()
        conn.close()

    def get_task(self, task_id: str) -> Optional[Dict]:
        """Retrieve task by ID"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_tasks(self, status: str = None, limit: int = 100) -> List[Dict]:
        """Retrieve tasks with optional filtering"""
        conn = self.connect()
        cursor = conn.cursor()

        if status:
            cursor.execute(
                "SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_audit_log(self, task_id: str) -> List[Dict]:
        """Get audit log for a task"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM audit_log WHERE task_id = ? ORDER BY timestamp",
            (task_id,)
        )

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM tasks")
        total_tasks = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE status = 'completed'")
        completed_tasks = cursor.fetchone()["count"]

        cursor.execute("SELECT SUM(execution_time_ms) as total FROM tasks WHERE execution_time_ms IS NOT NULL")
        total_execution_time = cursor.fetchone()["total"] or 0

        cursor.execute("SELECT SUM(tokens_input) as total FROM tasks WHERE tokens_input IS NOT NULL")
        total_tokens = cursor.fetchone()["total"] or 0

        conn.close()

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "total_execution_time_ms": total_execution_time,
            "total_tokens_used": total_tokens,
        }

    def cleanup_old_logs(self, days: int = 90):
        """Delete audit logs older than specified days"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM audit_log
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        """, (days,))

        conn.commit()
        deleted = cursor.rowcount
        conn.close()

        print(f"✓ Cleaned {deleted} old audit log entries (>{days} days)")
