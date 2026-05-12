"""Entity extraction from task inputs and outputs using Ollama"""

import json
import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
import sqlite3
from pathlib import Path

import ollama

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Extracted entity from task content"""
    name: str
    entity_type: str  # "threat", "technology", "concept", "framework", "topic", "role"
    category: str  # "security", "database", "compliance", "deployment", etc.
    confidence: float = 1.0
    description: Optional[str] = None


class EntityExtractor:
    """Extract entities from task inputs/outputs using Ollama 26B"""

    # Few-shot examples for entity extraction
    EXTRACTION_PROMPT = """You are an expert at extracting key concepts, technologies, threats, and frameworks from technical documentation.

Extract entities from the given text and return a JSON object with the following structure:
{
  "entities": [
    {
      "name": "entity name",
      "type": "threat|technology|concept|framework|topic|role",
      "category": "security|database|compliance|deployment|architecture|monitoring",
      "confidence": 0.9,
      "description": "brief description"
    }
  ]
}

EXAMPLES:
Input: "We need to implement GDPR compliance and encrypt all customer data at rest using AES-256"
Output: {
  "entities": [
    {"name": "GDPR", "type": "framework", "category": "compliance", "confidence": 0.99, "description": "General Data Protection Regulation"},
    {"name": "data encryption", "type": "concept", "category": "security", "confidence": 0.95, "description": "Encrypting data at rest"},
    {"name": "AES-256", "type": "technology", "category": "security", "confidence": 0.98, "description": "Advanced Encryption Standard 256-bit"}
  ]
}

Input: "SQL injection vulnerability detected in user authentication query"
Output: {
  "entities": [
    {"name": "SQL injection", "type": "threat", "category": "security", "confidence": 0.99, "description": "SQL query manipulation attack"},
    {"name": "authentication", "type": "concept", "category": "security", "confidence": 0.95, "description": "User identity verification"}
  ]
}

Now extract entities from this text:
TEXT:
{text}

Return ONLY valid JSON, no other text."""

    def __init__(self, model: str = "gemma2:26b", db_path: Optional[Path] = None):
        self.model = model
        self.client = ollama.Client(host="http://localhost:11434")
        self.db_path = db_path or (Path.home() / ".gemma-os" / "gemma_os.db")
        self.cache: Dict[str, List[Entity]] = {}

    def extract_entities(self, task_input: str, task_output: str) -> List[Entity]:
        """
        Extract entities from task input and output.

        Args:
            task_input: Input data/query for the task
            task_output: Output/result from the task

        Returns:
            List of extracted entities with confidence scores
        """
        combined_text = f"{task_input}\n\n{task_output}"

        # Check cache first
        cache_key = self._hash_text(combined_text)
        if cache_key in self.cache:
            logger.debug(f"Entity extraction cache hit for {cache_key[:16]}...")
            return self.cache[cache_key]

        # Extract entities using Ollama
        prompt = self.EXTRACTION_PROMPT.format(text=combined_text[:2000])  # Limit to 2000 chars

        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={
                    "temperature": 0.1,  # Low temperature for consistent extraction
                    "top_p": 0.5,        # Reduce randomness
                }
            )

            # Parse JSON response
            result_text = response['response'].strip()

            # Extract JSON from response (may be wrapped in text)
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                try:
                    data = json.loads(json_str)
                except json.JSONDecodeError as je:
                    logger.warning(f"JSON decode error: {str(je)}")
                    # Fallback: if no JSON found, return empty list
                    return []
            else:
                logger.warning(f"Could not find JSON in extraction: {result_text[:100]}")
                return []

            # Convert to Entity objects
            entities = []
            for item in data.get('entities', []):
                entity = Entity(
                    name=item['name'],
                    entity_type=item.get('type', 'concept'),
                    category=item.get('category', 'general'),
                    confidence=float(item.get('confidence', 0.8)),
                    description=item.get('description')
                )
                entities.append(entity)

            # Cache results
            self.cache[cache_key] = entities
            logger.info(f"Extracted {len(entities)} entities")

            return entities

        except Exception as e:
            logger.error(f"Entity extraction failed: {str(e)}")
            return []

    def store_entities(self, task_id: str, entities: List[Entity]) -> None:
        """
        Store extracted entities in the database.

        Args:
            task_id: ID of the task these entities came from
            entities: List of entities to store
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            for entity in entities:
                # Check if entity already exists
                cursor.execute(
                    "SELECT id FROM entities WHERE name = ? AND type = ?",
                    (entity.name, entity.entity_type)
                )
                result = cursor.fetchone()

                if result:
                    # Update existing entity
                    cursor.execute(
                        """UPDATE entities
                           SET frequency = frequency + 1,
                               last_seen = CURRENT_TIMESTAMP,
                               description = COALESCE(description, ?)
                           WHERE name = ? AND type = ?""",
                        (entity.description, entity.name, entity.entity_type)
                    )
                else:
                    # Insert new entity
                    cursor.execute(
                        """INSERT INTO entities
                           (name, type, category, description, frequency, first_seen, last_seen)
                           VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
                        (entity.name, entity.entity_type, entity.category, entity.description)
                    )

                # Link task to entity in graph
                entity_id = cursor.lastrowid if not result else result[0]
                cursor.execute(
                    """INSERT INTO task_entities (task_id, entity_id, confidence)
                       VALUES (?, ?, ?)
                       ON CONFLICT(task_id, entity_id) DO UPDATE SET confidence = ?""",
                    (task_id, entity_id, entity.confidence, entity.confidence)
                )

            conn.commit()
            conn.close()
            logger.info(f"Stored {len(entities)} entities for task {task_id}")

        except Exception as e:
            logger.error(f"Failed to store entities: {str(e)}")

    @staticmethod
    def _hash_text(text: str) -> str:
        """Create a simple hash of text for caching"""
        import hashlib
        return hashlib.md5(text.encode()).hexdigest()
