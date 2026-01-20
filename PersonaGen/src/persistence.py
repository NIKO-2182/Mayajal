"""
SQLite persistence layer for artifacts
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
import json
from .models import Artifact


class SQLiteDB:
    """SQLite database wrapper for artifacts"""

    def __init__(self, db_path: str = "artifacts.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file (or ":memory:" for in-memory)
        """
        self.db_path = db_path
        self.is_memory = db_path == ":memory:"
        self._memory_conn = None
        
        # Initialize schema
        self._init_schema()

    def _init_schema(self):
        """Create tables if they don't exist"""
        with self.conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS artifacts (
                    id TEXT PRIMARY KEY,
                    persona_slug TEXT NOT NULL,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    file_extension TEXT,
                    created_at TEXT,
                    modified_at TEXT,
                    metadata TEXT,
                    FOREIGN KEY (persona_slug) REFERENCES personas(slug)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS personas (
                    slug TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    role TEXT,
                    company TEXT,
                    location TEXT,
                    created_at TEXT,
                    data TEXT
                )
            """)
            
            # Create indices
            conn.execute("CREATE INDEX IF NOT EXISTS idx_persona_slug ON artifacts(persona_slug)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON artifacts(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON artifacts(created_at)")
            
            conn.commit()

    @contextmanager
    def conn(self):
        """Context manager for database connections"""
        if self.is_memory:
            if self._memory_conn is None:
                self._memory_conn = sqlite3.connect(":memory:")
            yield self._memory_conn
        else:
            connection = sqlite3.connect(self.db_path)
            try:
                yield connection
            finally:
                connection.close()

    def insert_artifact(self, artifact: Artifact) -> bool:
        """Insert single artifact"""
        try:
            with self.conn() as conn:
                conn.execute("""
                    INSERT INTO artifacts 
                    (id, persona_slug, category, title, content, file_extension, 
                     created_at, modified_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    artifact.artifact_id,
                    artifact.persona_slug,
                    artifact.category,
                    artifact.title,
                    artifact.content,
                    artifact.file_extension,
                    artifact.created_at.isoformat(),
                    artifact.modified_at.isoformat(),
                    json.dumps(artifact.metadata),
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error inserting artifact: {e}")
            return False

    def insert_artifacts_batch(self, artifacts: List[Artifact]) -> int:
        """Insert multiple artifacts"""
        count = 0
        with self.conn() as conn:
            for artifact in artifacts:
                try:
                    conn.execute("""
                        INSERT INTO artifacts 
                        (id, persona_slug, category, title, content, file_extension, 
                         created_at, modified_at, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        artifact.artifact_id,
                        artifact.persona_slug,
                        artifact.category,
                        artifact.title,
                        artifact.content,
                        artifact.file_extension,
                        artifact.created_at.isoformat(),
                        artifact.modified_at.isoformat(),
                        json.dumps(artifact.metadata),
                    ))
                    count += 1
                except Exception as e:
                    print(f"Error inserting artifact: {e}")
            conn.commit()
        return count

    def get_artifacts_by_persona(self, persona_slug: str) -> List[Artifact]:
        """Get all artifacts for a persona"""
        with self.conn() as conn:
            rows = conn.execute("""
                SELECT id, persona_slug, category, title, content, file_extension,
                       created_at, modified_at, metadata
                FROM artifacts
                WHERE persona_slug = ?
                ORDER BY created_at DESC
            """, (persona_slug,)).fetchall()
            
            artifacts = []
            for row in rows:
                artifacts.append(self._row_to_artifact(row))
            return artifacts

    def get_all_personas(self) -> List[str]:
        """Get all persona slugs"""
        with self.conn() as conn:
            rows = conn.execute("""
                SELECT DISTINCT persona_slug FROM artifacts
                ORDER BY persona_slug
            """).fetchall()
            return [row[0] for row in rows]

    def delete_all(self):
        """Clear all data"""
        with self.conn() as conn:
            conn.execute("DELETE FROM artifacts")
            conn.execute("DELETE FROM personas")
            conn.commit()

    @staticmethod
    def _row_to_artifact(row: tuple) -> Artifact:
        """Convert database row to Artifact object"""
        from datetime import datetime
        
        return Artifact(
            artifact_id=row[0],
            persona_slug=row[1],
            category=row[2],
            title=row[3],
            content=row[4],
            file_extension=row[5],
            created_at=datetime.fromisoformat(row[6]),
            modified_at=datetime.fromisoformat(row[7]),
            metadata=json.loads(row[8]) if row[8] else {},
        )
