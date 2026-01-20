"""
Batch generation with async support
"""

import asyncio
from typing import List, Optional
from .models import Artifact, PersonaContext, GenerationConfig
from .persistence import SQLiteDB
from .gemini_provider import GeminiProvider
from .prompts import PromptFactory


class BatchGenerator:
    """Generate artifacts in batches with concurrency control"""

    def __init__(self, db: Optional[SQLiteDB] = None, max_concurrent: int = 3):
        """
        Initialize batch generator
        
        Args:
            db: SQLiteDB instance for persistence
            max_concurrent: Max concurrent requests
        """
        self.db = db or SQLiteDB()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.prompt_factory = PromptFactory()

    async def generate_batch(
        self,
        persona: PersonaContext,
        config: GenerationConfig,
        provider: GeminiProvider,
    ) -> List[Artifact]:
        """
        Generate a batch of artifacts for a persona
        
        Args:
            persona: PersonaContext
            config: GenerationConfig
            provider: GeminiProvider instance
            
        Returns:
            List of generated Artifacts
        """
        # Build prompt
        prompt = self.prompt_factory.build_generation_prompt(persona, config)
        
        # Call Gemini (throttled by semaphore)
        async with self.semaphore:
            artifacts_data = await asyncio.to_thread(
                provider.generate_artifacts,
                prompt,
                config.num_artifacts,
                config.temperature,
                config.max_tokens,
            )

        # Convert to Artifact objects
        artifacts = []
        for data in artifacts_data:
            try:
                artifact = Artifact(
                    persona_slug=persona.slug,
                    category=data.get("category", "code"),
                    title=data.get("title", "untitled"),
                    content=data.get("content", ""),
                    file_extension=data.get("file_extension", ".py"),
                )
                artifacts.append(artifact)
            except Exception as e:
                print(f"Error creating artifact: {e}")

        return artifacts

    async def generate_multiple_personas(
        self,
        personas: List[PersonaContext],
        config: GenerationConfig,
        provider: GeminiProvider,
    ) -> int:
        """
        Generate artifacts for multiple personas in parallel
        
        Args:
            personas: List of PersonaContext
            config: GenerationConfig
            provider: GeminiProvider instance
            
        Returns:
            Total artifacts generated
        """
        tasks = [
            self.generate_batch(persona, config, provider)
            for persona in personas
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total = 0
        for result in results:
            if isinstance(result, list):
                count = self.db.insert_artifacts_batch(result)
                total += count

        return total
