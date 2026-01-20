"""
Post-processing and validation of generated artifacts
"""

import ast
import json
from typing import List, Tuple
from .models import Artifact
from .persistence import SQLiteDB


class PostProcessor:
    """Validates and processes artifacts"""

    def __init__(self, db: SQLiteDB):
        """
        Initialize post-processor
        
        Args:
            db: SQLiteDB instance
        """
        self.db = db

    def validate_artifact(self, artifact: Artifact) -> bool:
        """
        Validate a single artifact
        
        Args:
            artifact: Artifact to validate
            
        Returns:
            True if valid
        """
        # Check content length
        if not artifact.content or len(artifact.content) < 10:
            return False

        # Check syntax based on file extension
        if artifact.file_extension == ".py":
            try:
                ast.parse(artifact.content)
            except SyntaxError:
                return False
        
        elif artifact.file_extension == ".json":
            try:
                json.loads(artifact.content)
            except json.JSONDecodeError:
                return False

        return True

    def process_batch(self, artifacts: List[Artifact]) -> Tuple[int, int]:
        """
        Validate and persist a batch of artifacts
        
        Args:
            artifacts: List of artifacts
            
        Returns:
            Tuple of (success_count, failure_count)
        """
        valid_artifacts = []
        failed = 0

        for artifact in artifacts:
            if self.validate_artifact(artifact):
                valid_artifacts.append(artifact)
            else:
                failed += 1

        # Persist valid artifacts
        success = self.db.insert_artifacts_batch(valid_artifacts)
        
        return success, failed
