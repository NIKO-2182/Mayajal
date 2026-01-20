"""
Persona builder - enriches descriptions into rich personas
"""

from typing import Optional
from .models import PersonaContext
import random
import re


class PersonaBuilder:
    """Builds rich personas from simple descriptions"""

    ROLES = [
        "Backend Engineer",
        "Frontend Developer",
        "DevOps Engineer",
        "ML Engineer",
        "Data Engineer",
        "Full Stack Developer",
        "Security Engineer",
        "Cloud Architect",
        "SRE",
        "Database Administrator",
    ]

    COMPANIES = [
        "TechCorp",
        "CloudDynamics",
        "DataFlow Systems",
        "VentureAI",
        "SecureNet",
        "InnovateTech",
        "QuantumLeap",
        "NeuralWorks",
    ]

    LOCATIONS = [
        "San Francisco, CA",
        "New York, NY",
        "Austin, TX",
        "Seattle, WA",
        "Boston, MA",
        "Denver, CO",
        "Portland, OR",
        "Remote",
    ]

    TECH_STACKS = {
        "Backend": ["Python", "Go", "Rust", "Node.js", "Java"],
        "Frontend": ["React", "Vue", "Angular", "TypeScript"],
        "DevOps": ["Kubernetes", "Docker", "Terraform", "Jenkins"],
        "Data": ["Pandas", "Spark", "SQL", "TensorFlow"],
    }

    QUIRKS = [
        "Coffee addict",
        "Night owl",
        "Open source enthusiast",
        "Tech blogger",
        "Podcast listener",
        "Terminal lover",
        "Documentation focused",
    ]

    def __init__(self):
        pass

    def enrich(
        self,
        description: str,
        seed: Optional[int] = None
    ) -> PersonaContext:
        """
        Enrich a simple description into a rich persona
        
        Args:
            description: Short description (e.g., "Senior Python engineer")
            seed: Optional seed for reproducibility
            
        Returns:
            PersonaContext with enriched data
        """
        if seed is not None:
            random.seed(seed)

        # Extract role from description or use random
        role = self._extract_role(description)
        
        # Generate name and slug
        name = self._generate_name()
        slug = self._name_to_slug(name)

        # Pick random attributes
        company = random.choice(self.COMPANIES)
        location = random.choice(self.LOCATIONS)
        experience_years = random.randint(2, 15)
        
        # Get tech stack
        stack_category = random.choice(list(self.TECH_STACKS.keys()))
        tech_stack = random.sample(
            self.TECH_STACKS[stack_category],
            k=random.randint(2, 4)
        )
        
        # Get quirks
        quirks = random.sample(self.QUIRKS, k=random.randint(1, 3))

        # Generate email and github
        email = f"{slug}@{company.lower().replace(' ', '')}.com"
        github = slug.replace("-", "")

        return PersonaContext(
            name=name,
            slug=slug,
            description=description,
            role=role,
            company=company,
            location=location,
            experience_years=experience_years,
            tech_stack=tech_stack,
            quirks=quirks,
            email=email,
            github_username=github,
        )

    def _extract_role(self, description: str) -> str:
        """Extract role from description"""
        description_lower = description.lower()
        
        for role in self.ROLES:
            if role.lower() in description_lower:
                return role
        
        # Default to first word capitalized
        words = description.strip().split()
        if words:
            return f"{words[0].capitalize()} Engineer"
        
        return random.choice(self.ROLES)

    def _generate_name(self) -> str:
        """Generate a random name"""
        first_names = [
            "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank",
            "Grace", "Henry", "Isabel", "Jack", "Karen", "Leo"
        ]
        last_names = [
            "Johnson", "Smith", "Williams", "Brown", "Jones",
            "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"
        ]
        
        first = random.choice(first_names)
        last = random.choice(last_names)
        return f"{first} {last}"

    def _name_to_slug(self, name: str) -> str:
        """Convert name to URL-friendly slug"""
        return name.lower().replace(" ", "-")
