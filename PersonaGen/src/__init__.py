"""
Artifact Persona Generator - Main package
"""

__version__ = "0.1.0"
__author__ = "PersonaGen"

from .models import Artifact, PersonaContext, GenerationConfig
from .persona import PersonaBuilder
from .persistence import SQLiteDB
from .gemini_provider import GeminiProvider
from .prompts import PromptFactory
from .batcher import BatchGenerator

__all__ = [
    "Artifact",
    "PersonaContext",
    "GenerationConfig",
    "PersonaBuilder",
    "SQLiteDB",
    "GeminiProvider",
    "PromptFactory",
    "BatchGenerator",
]
