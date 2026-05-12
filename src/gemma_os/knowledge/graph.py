"""Knowledge graph data model and management"""

import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple, Any

logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """Node in the knowledge graph"""
    node_id: str
    node_type: str  # "task", "entity", "summary"
    label: str
    created_at: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


@dataclass
class GraphEdge:
    """Relationship edge in the knowledge graph"""
    source_id: str
    target_id: str
    relationship_type: str  # "mentions", "related_to", "builds_on", "contradicts", "depends_on"
    weight: float = 1.0
    confidence: float = 0.8


class KnowledgeGraph:
    """Build and manage knowledge graph from task history"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (Path.home() / ".gemma-os" / "gemma_os.db")
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []

    def init_schema(self) -> None:
        """Initialize graph tables in database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Entities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    type TEXT NOT NULL,
                    category TEXT,
                    description TEXT,
                    frequency INTEGER DEFAULT 1,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_category ON entities(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_frequency ON entities(frequency DESC)")

            # Task-Entity linking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    entity_id INTEGER NOT NULL,
                    confidence FLOAT DEFAULT 1.0,
                    FOREIGN KEY (entity_id) REFERENCES entities(id),
                    UNIQUE(task_id, entity_id)
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_entities_task ON task_entities(task_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_entities_entity ON task_entities(entity_id)")

            # Graph nodes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS graph_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_type TEXT NOT NULL,
                    node_id TEXT UNIQUE NOT NULL,
                    label TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data BLOB
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_graph_nodes_type ON graph_nodes(node_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_graph_nodes_id ON graph_nodes(node_id)")

            # Graph edges
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS graph_edges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_node_id TEXT NOT NULL,
                    target_node_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    weight FLOAT DEFAULT 1.0,
                    confidence FLOAT DEFAULT 0.8,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_node_id) REFERENCES graph_nodes(node_id),
                    FOREIGN KEY (target_node_id) REFERENCES graph_nodes(node_id)
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_source ON graph_edges(source_node_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_target ON graph_edges(target_node_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_type ON graph_edges(relationship_type)")

            # Task summaries (for memory consolidation)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_task_ids TEXT NOT NULL,
                    summary_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    consolidated_at TIMESTAMP
                )
            """)

            conn.commit()
            conn.close()
            logger.info("Knowledge graph schema initialized")

        except Exception as e:
            logger.error(f"Failed to initialize graph schema: {str(e)}")

    def add_task_node(self, task_id: str, label: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a task node to the graph"""
        node = GraphNode(
            node_id=task_id,
            node_type="task",
            label=label,
            created_at=datetime.now().isoformat(),
            data=metadata or {}
        )
        self._save_node(node)

    def add_entity_node(self, entity_name: str, entity_type: str, category: str) -> None:
        """Add an entity node to the graph"""
        node = GraphNode(
            node_id=entity_name,
            node_type="entity",
            label=entity_name,
            created_at=datetime.now().isoformat(),
            data={"type": entity_type, "category": category}
        )
        self._save_node(node)

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        rel_type: str,
        weight: float = 1.0,
        confidence: float = 0.8
    ) -> None:
        """Add a relationship edge between two nodes"""
        edge = GraphEdge(
            source_id=source_id,
            target_id=target_id,
            relationship_type=rel_type,
            weight=weight,
            confidence=confidence
        )
        self._save_edge(edge)

    def build_graph_from_task(self, task_id: str, entities: List[Any]) -> None:
        """
        Build graph connections for a task and its extracted entities.

        Args:
            task_id: ID of the task
            entities: List of extracted Entity objects
        """
        # Add task node
        self.add_task_node(task_id, f"Task: {task_id}")

        for entity in entities:
            # Add entity node
            self.add_entity_node(entity.name, entity.entity_type, entity.category)

            # Create task→entity relationship
            self.add_relationship(
                source_id=task_id,
                target_id=entity.name,
                rel_type="mentions",
                weight=1.0,
                confidence=entity.confidence
            )

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

    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Count nodes
            cursor.execute("SELECT COUNT(*) FROM graph_nodes")
            node_count = cursor.fetchone()[0]

            # Count edges
            cursor.execute("SELECT COUNT(*) FROM graph_edges")
            edge_count = cursor.fetchone()[0]

            # Count entities
            cursor.execute("SELECT COUNT(*) FROM entities")
            entity_count = cursor.fetchone()[0]

            # Count task-entity relationships
            cursor.execute("SELECT COUNT(*) FROM task_entities")
            task_entity_count = cursor.fetchone()[0]

            conn.close()

            return {
                "nodes": node_count,
                "edges": edge_count,
                "entities": entity_count,
                "task_entities": task_entity_count,
            }

        except Exception as e:
            logger.error(f"Failed to get graph stats: {str(e)}")
            return {}

    def _save_node(self, node: GraphNode) -> None:
        """Save a node to the database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            data_json = json.dumps(node.data) if node.data else None

            cursor.execute("""
                INSERT OR REPLACE INTO graph_nodes
                (node_type, node_id, label, created_at, data)
                VALUES (?, ?, ?, ?, ?)
            """, (node.node_type, node.node_id, node.label, node.created_at, data_json))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Failed to save node: {str(e)}")

    def _save_edge(self, edge: GraphEdge) -> None:
        """Save an edge to the database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO graph_edges
                (source_node_id, target_node_id, relationship_type, weight, confidence)
                VALUES (?, ?, ?, ?, ?)
            """, (
                edge.source_id,
                edge.target_id,
                edge.relationship_type,
                edge.weight,
                edge.confidence
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Failed to save edge: {str(e)}")
