"""Memory consolidation and long-term memory management"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

import ollama

logger = logging.getLogger(__name__)


class MemoryConsolidator:
    """Consolidate and manage long-term memory through task summarization"""

    def __init__(self, model: str = "gemma2:2b", db_path: Optional[Path] = None):
        """
        Args:
            model: Ollama model to use for summarization (use 2B for speed)
            db_path: Path to SQLite database
        """
        self.model = model
        self.client = ollama.Client(host="http://localhost:11434")
        self.db_path = db_path or (Path.home() / ".gemma-os" / "gemma_os.db")

    def consolidate_memory(
        self,
        older_than_days: int = 30,
        min_tasks_per_summary: int = 5,
    ) -> int:
        """
        Consolidate old tasks into summaries to save memory.

        Maintains high-fidelity recent history while summarizing older tasks.

        Args:
            older_than_days: Consolidate tasks older than this many days
            min_tasks_per_summary: Minimum tasks to group into one summary

        Returns:
            Number of tasks consolidated
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Find old tasks that haven't been consolidated
            cutoff_date = (datetime.now() - timedelta(days=older_than_days)).isoformat()

            cursor.execute("""
                SELECT task_id, task_name, output_data, execution_time_ms
                FROM tasks
                WHERE created_at < ?
                  AND status = 'completed'
                ORDER BY created_at ASC
            """, (cutoff_date,))

            old_tasks = cursor.fetchall()

            if len(old_tasks) < min_tasks_per_summary:
                logger.info(f"Not enough old tasks to consolidate ({len(old_tasks)})")
                return 0

            # Group tasks by category/type and summarize
            tasks_consolidated = 0

            for i in range(0, len(old_tasks), min_tasks_per_summary):
                batch = old_tasks[i:i + min_tasks_per_summary]
                summary_text = self._generate_summary(batch)

                if summary_text:
                    # Store summary
                    task_ids = [t[0] for t in batch]
                    self._store_summary(task_ids, summary_text)
                    tasks_consolidated += len(batch)
                    logger.info(f"Consolidated {len(batch)} tasks into summary")

            conn.close()
            return tasks_consolidated

        except Exception as e:
            logger.error(f"Failed to consolidate memory: {str(e)}")
            return 0

    def _generate_summary(self, task_batch: List[tuple]) -> Optional[str]:
        """
        Generate a summary of multiple tasks.

        Args:
            task_batch: List of task tuples (task_id, task_name, output_data, execution_time_ms)

        Returns:
            Summary text or None if generation fails
        """
        try:
            # Create prompt for summarization
            tasks_text = "\n\n".join([
                f"Task: {task[1]}\n{task[2][:500]}"
                for task in task_batch
                if task[2]
            ])

            prompt = f"""Summarize the following {len(task_batch)} completed tasks into a concise paragraph that captures:
- The main objectives
- Key findings or outputs
- Common patterns across tasks

Tasks:
{tasks_text}

Provide a 2-3 sentence summary:"""

            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={"temperature": 0.3}
            )

            summary = response['response'].strip()
            logger.debug(f"Generated summary: {summary[:100]}...")
            return summary

        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            return None

    def _store_summary(self, task_ids: List[str], summary_text: str) -> None:
        """Store a summary in the database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO task_summaries
                (original_task_ids, summary_text, consolidated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (json.dumps(task_ids), summary_text))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Failed to store summary: {str(e)}")

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory usage and consolidation"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Count original tasks
            cursor.execute("SELECT COUNT(*) FROM tasks")
            total_tasks = cursor.fetchone()[0]

            # Count consolidated summaries
            cursor.execute("SELECT COUNT(*) FROM task_summaries")
            summaries = cursor.fetchone()[0]

            # Count tasks in summaries
            cursor.execute("""
                SELECT SUM(json_array_length(original_task_ids))
                FROM task_summaries
            """)
            consolidated_tasks_row = cursor.fetchone()
            consolidated_tasks = consolidated_tasks_row[0] or 0

            # Database size (approximate)
            cursor.execute("""
                SELECT SUM(pgsize) FROM (
                    SELECT pgsize FROM dbstat
                    UNION ALL
                    SELECT 0 as pgsize
                ) WHERE pgsize > 0
            """)
            db_size_row = cursor.fetchone()
            db_size = db_size_row[0] or 0

            conn.close()

            return {
                "total_tasks": total_tasks,
                "active_tasks": total_tasks - consolidated_tasks,
                "consolidated_tasks": consolidated_tasks,
                "summaries": summaries,
                "database_size_bytes": db_size,
                "consolidation_ratio": (
                    (consolidated_tasks / total_tasks * 100)
                    if total_tasks > 0 else 0
                ),
            }

        except Exception as e:
            logger.error(f"Failed to get memory stats: {str(e)}")
            return {}

    def get_relevant_context(self, entity_name: str, max_tasks: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most relevant context (tasks or summaries) for a given entity.

        Args:
            entity_name: Entity to get context for
            max_tasks: Maximum tasks/summaries to return

        Returns:
            List of relevant task outputs or summaries
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            context = []

            # Get recent tasks mentioning this entity
            cursor.execute("""
                SELECT DISTINCT t.task_id, t.output_data, t.created_at
                FROM tasks t
                JOIN task_entities te ON t.task_id = te.task_id
                JOIN entities e ON te.entity_id = e.id
                WHERE e.name = ?
                ORDER BY t.created_at DESC
                LIMIT ?
            """, (entity_name, max_tasks))

            for task_id, output, created_at in cursor.fetchall():
                context.append({
                    "type": "task",
                    "task_id": task_id,
                    "content": output,
                    "date": created_at,
                })

            # If not enough recent tasks, add summaries
            if len(context) < max_tasks:
                cursor.execute("""
                    SELECT summary_text, consolidated_at
                    FROM task_summaries
                    ORDER BY consolidated_at DESC
                    LIMIT ?
                """, (max_tasks - len(context),))

                for summary, consolidated_at in cursor.fetchall():
                    context.append({
                        "type": "summary",
                        "content": summary,
                        "date": consolidated_at,
                    })

            conn.close()
            return context

        except Exception as e:
            logger.error(f"Failed to get relevant context: {str(e)}")
            return []
