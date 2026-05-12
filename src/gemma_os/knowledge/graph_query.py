"""Graph querying and reasoning for intelligent task retrieval"""

import logging
import sqlite3
from collections import deque, defaultdict
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple, Any

logger = logging.getLogger(__name__)


class GraphQuery:
    """Query and reason over the knowledge graph"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (Path.home() / ".gemma-os" / "gemma_os.db")

    def get_entity_frequency(self) -> Dict[str, int]:
        """Get frequency count of all entities"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute("""
                SELECT name, frequency FROM entities ORDER BY frequency DESC
            """)

            result = {row[0]: row[1] for row in cursor.fetchall()}
            conn.close()
            return result

        except Exception as e:
            logger.error(f"Failed to get entity frequency: {str(e)}")
            return {}

    def find_related_tasks(self, task_id: str, max_hops: int = 2, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find tasks related to a given task through shared entities.

        Graph traversal pattern:
        Task A → Entity X → Task B (1 hop)
        Task A → Entity X → Entity Y → Task B (2 hops)

        Args:
            task_id: ID of the task to find relations for
            max_hops: Maximum hops in graph (default 2)
            limit: Maximum tasks to return

        Returns:
            List of related task IDs ordered by relationship strength
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            related_tasks: Dict[str, float] = defaultdict(float)

            # Get entities for source task
            cursor.execute("""
                SELECT e.name, te.confidence
                FROM task_entities te
                JOIN entities e ON te.entity_id = e.id
                WHERE te.task_id = ?
            """, (task_id,))

            source_entities = [(row[0], row[1]) for row in cursor.fetchall()]

            if not source_entities:
                logger.debug(f"No entities found for task {task_id}")
                return []

            # BFS to find related tasks through entity hops
            visited: Set[str] = {task_id}
            current_level = {entity[0]: entity[1] for entity in source_entities}

            for hop in range(max_hops):
                next_level: Dict[str, float] = {}

                for entity_name, entity_weight in current_level.items():
                    # Find tasks that mention this entity
                    cursor.execute("""
                        SELECT DISTINCT te.task_id, te.confidence
                        FROM task_entities te
                        JOIN entities e ON te.entity_id = e.id
                        WHERE e.name = ? AND te.task_id != ?
                    """, (entity_name, task_id))

                    for related_task_id, confidence in cursor.fetchall():
                        if related_task_id not in visited:
                            # Accumulate relationship strength
                            weight = entity_weight * confidence * (1.0 / (hop + 1))
                            related_tasks[related_task_id] += weight
                            visited.add(related_task_id)

                    # Find related entities
                    cursor.execute("""
                        SELECT DISTINCT e2.name, COUNT(*) as co_occurrence
                        FROM task_entities te1
                        JOIN task_entities te2 ON te1.task_id = te2.task_id
                        JOIN entities e1 ON te1.entity_id = e1.id
                        JOIN entities e2 ON te2.entity_id = e2.id
                        WHERE e1.name = ? AND e2.name != ?
                        GROUP BY e2.name
                        ORDER BY co_occurrence DESC
                    """, (entity_name, entity_name))

                    for next_entity, co_occurrence in cursor.fetchall():
                        if next_entity not in next_level:
                            next_level[next_entity] = entity_weight * (co_occurrence / 10.0)

                current_level = next_level

                if not current_level:
                    break

            # Sort by relationship weight and return
            sorted_tasks = sorted(related_tasks.items(), key=lambda x: x[1], reverse=True)

            # Fetch task details
            result = []
            for related_task_id, weight in sorted_tasks[:limit]:
                cursor.execute("""
                    SELECT task_id, task_name, output_data, execution_time_ms
                    FROM tasks
                    WHERE task_id = ?
                """, (related_task_id,))

                task_row = cursor.fetchone()
                if task_row:
                    result.append({
                        "task_id": task_row[0],
                        "task_name": task_row[1],
                        "summary": task_row[2][:500] if task_row[2] else "",
                        "execution_time_ms": task_row[3],
                        "relationship_weight": weight,
                    })

            conn.close()
            return result

        except Exception as e:
            logger.error(f"Failed to find related tasks: {str(e)}")
            return []

    def find_related_entities(self, entity_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find semantically related entities based on co-occurrence.

        Args:
            entity_name: Name of the entity to find relations for
            limit: Maximum entities to return

        Returns:
            List of related entities with co-occurrence scores
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Find entities that co-occur with this entity
            cursor.execute("""
                SELECT e2.name, e2.type, e2.category, COUNT(*) as co_occurrence
                FROM task_entities te1
                JOIN task_entities te2 ON te1.task_id = te2.task_id
                JOIN entities e1 ON te1.entity_id = e1.id
                JOIN entities e2 ON te2.entity_id = e2.id
                WHERE e1.name = ? AND e2.name != ?
                GROUP BY e2.name
                ORDER BY co_occurrence DESC
                LIMIT ?
            """, (entity_name, entity_name, limit))

            result = []
            for row in cursor.fetchall():
                result.append({
                    "name": row[0],
                    "type": row[1],
                    "category": row[2],
                    "co_occurrence": row[3],
                })

            conn.close()
            return result

        except Exception as e:
            logger.error(f"Failed to find related entities: {str(e)}")
            return []

    def recommend_related_tasks(self, current_task_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Recommend tasks based on current task.

        Args:
            current_task_id: ID of the current task
            limit: Maximum recommendations to return

        Returns:
            List of recommended tasks
        """
        related = self.find_related_tasks(current_task_id, max_hops=2, limit=limit * 2)

        # Filter for highest relevance
        recommendations = []
        for task in related[:limit]:
            recommendations.append({
                "task_id": task["task_id"],
                "task_name": task["task_name"],
                "summary": task["summary"],
                "relevance_score": task["relationship_weight"],
            })

        return recommendations

    def find_path(self, source_entity: str, target_entity: str) -> List[str]:
        """
        Find shortest path between two entities in the graph.

        Uses BFS to find the shortest conceptual path.

        Args:
            source_entity: Starting entity name
            target_entity: Target entity name

        Returns:
            List of entity names forming the path, or empty if no path exists
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # BFS to find shortest path
            queue = deque([(source_entity, [source_entity])])
            visited: Set[str] = {source_entity}

            while queue:
                current, path = queue.popleft()

                if current == target_entity:
                    conn.close()
                    return path

                # Find connected entities
                cursor.execute("""
                    SELECT DISTINCT e2.name
                    FROM task_entities te1
                    JOIN task_entities te2 ON te1.task_id = te2.task_id
                    JOIN entities e1 ON te1.entity_id = e1.id
                    JOIN entities e2 ON te2.entity_id = e2.id
                    WHERE e1.name = ?
                """, (current,))

                for (next_entity,) in cursor.fetchall():
                    if next_entity not in visited:
                        visited.add(next_entity)
                        queue.append((next_entity, path + [next_entity]))

            conn.close()
            logger.debug(f"No path found between {source_entity} and {target_entity}")
            return []

        except Exception as e:
            logger.error(f"Failed to find path: {str(e)}")
            return []

    def get_entity_summary(self, entity_name: str) -> Dict[str, Any]:
        """
        Get comprehensive summary of an entity.

        Args:
            entity_name: Name of the entity

        Returns:
            Dictionary with entity info and related context
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Get entity info
            cursor.execute("""
                SELECT id, type, category, description, frequency, first_seen, last_seen
                FROM entities
                WHERE name = ?
            """, (entity_name,))

            entity_row = cursor.fetchone()
            if not entity_row:
                return {}

            entity_id, etype, category, description, frequency, first_seen, last_seen = entity_row

            # Get related entities
            related_entities = self.find_related_entities(entity_name, limit=5)

            # Get tasks mentioning this entity
            cursor.execute("""
                SELECT DISTINCT te.task_id
                FROM task_entities te
                WHERE te.entity_id = ?
                ORDER BY te.confidence DESC
                LIMIT 5
            """, (entity_id,))

            related_tasks = [row[0] for row in cursor.fetchall()]

            conn.close()

            return {
                "name": entity_name,
                "type": etype,
                "category": category,
                "description": description,
                "frequency": frequency,
                "first_seen": first_seen,
                "last_seen": last_seen,
                "related_entities": related_entities,
                "related_tasks": related_tasks,
            }

        except Exception as e:
            logger.error(f"Failed to get entity summary: {str(e)}")
            return {}

    def search_entities(self, query: str, entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for entities by name or description.

        Args:
            query: Search query (partial entity name)
            entity_type: Optional filter by entity type

        Returns:
            List of matching entities
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            sql = """
                SELECT name, type, category, frequency, description
                FROM entities
                WHERE name LIKE ? OR description LIKE ?
            """
            params = (f"%{query}%", f"%{query}%")

            if entity_type:
                sql += " AND type = ?"
                params = (f"%{query}%", f"%{query}%", entity_type)

            sql += " ORDER BY frequency DESC LIMIT 10"

            cursor.execute(sql, params)

            result = []
            for row in cursor.fetchall():
                result.append({
                    "name": row[0],
                    "type": row[1],
                    "category": row[2],
                    "frequency": row[3],
                    "description": row[4],
                })

            conn.close()
            return result

        except Exception as e:
            logger.error(f"Failed to search entities: {str(e)}")
            return []
