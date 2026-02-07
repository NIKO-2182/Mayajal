"""
Data models for the persona generator system
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4


class GenerationConfig(BaseModel):
    """Configuration for artifact generation"""
    
    num_artifacts: int = Field(default=25, ge=1, le=500)
    temperature: float = Field(default=0.75, ge=0.0, le=1.0)
    max_tokens: int = Field(default=20000, ge=100, le=4000)
    seed: Optional[int] = None
    categories: List[str] = Field(default_factory=lambda: ["code", "config", "docs"])
    model: str = "gemini-2.5-flash"

    class Config:
        json_schema_extra = {
            "example": {
                "num_artifacts": 25,
                "temperature": 0.75,
                "max_tokens": 20000,
                "categories": ["code", "config"]
            }
        }


class PersonaContext(BaseModel):
    """Rich context for a single persona"""
    
    persona_id: str = Field(default_factory=lambda: str(uuid4())[:8])
    name: str
    slug: str
    description: str
    role: str
    company: str
    location: str
    experience_years: int = 5
    primary_language: str = "Python"
    tech_stack: List[str] = Field(default_factory=list)
    quirks: List[str] = Field(default_factory=list)
    email: str = ""
    github_username: str = ""

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Alice Johnson",
                "slug": "alice-johnson",
                "role": "Backend Engineer",
                "company": "TechCorp",
                "location": "San Francisco, CA"
            }
        }

    def to_context_string(self) -> str:
        """Convert to string for prompt injection"""
        return f"""
Persona: {self.name} ({self.slug})
Role: {self.role}
Company: {self.company}
Experience: {self.experience_years} years
Tech Stack: {', '.join(self.tech_stack)}
Location: {self.location}
"""


class Artifact(BaseModel):
    """Single generated artifact"""
    
    artifact_id: str = Field(default_factory=lambda: str(uuid4()))
    persona_slug: str
    category: str  # "code", "config", "docs", etc.
    title: str
    content: str
    file_extension: str = ".py"
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = self.dict()
        data["created_at"] = self.created_at.isoformat()
        data["modified_at"] = self.modified_at.isoformat()
        return data


class EvaluationMetrics(BaseModel):
    """Quality metrics for a batch of artifacts"""
    
    batch_id: str = Field(default_factory=lambda: str(uuid4())[:8])
    total_artifacts: int
    success_count: int
    validity_rate: float
    diversity_score: float
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }