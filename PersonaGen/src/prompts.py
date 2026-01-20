"""
Prompt templates for artifact generation
"""

from typing import Optional
from .models import PersonaContext, GenerationConfig
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate


class PromptFactory:
    """Factory for creating generation prompts"""

    SYSTEM_PROMPT = """You are an expert developer generating realistic digital artifacts.
Create authentic-looking code, configurations, and documentation that a {role} would write.
Ensure artifacts are realistic, consistent, and contextually appropriate."""

    def __init__(self):
        pass

    def build_generation_prompt(
        self,
        persona: PersonaContext,
        config: GenerationConfig,
        prior_artifacts: Optional[str] = None,
    ) -> str:
        """
        Build full generation prompt with persona context
        
        Args:
            persona: PersonaContext for the persona
            config: GenerationConfig for generation settings
            prior_artifacts: Optional context of prior artifacts
            
        Returns:
            Full prompt string
        """
        prompt = f"""Generate exactly {config.num_artifacts} realistic artifacts for:

{persona.to_context_string()}

Categories: {', '.join(config.categories)}
Format: Return a JSON array with exactly {config.num_artifacts} artifacts.

Each artifact must have:
- title: Descriptive name
- category: {'/'.join(config.categories)}
- file_extension: .py, .yaml, .md, etc.
- content: Realistic artifact content

"""
        
        if prior_artifacts:
            prompt += f"\nConsider these prior artifacts for consistency:\n{prior_artifacts}\n"

        prompt += f"""
Return ONLY valid JSON array. Start with [ and end with ].
Example format:
[
  {{
    "title": "deployment.yaml",
    "category": "config",
    "file_extension": ".yaml",
    "content": "..."
  }},
  ...
]

IMPORTANT: 
- Use consistent naming/style across all artifacts
- Include authentic technical details
- Make content realistic and properly formatted
"""
        
        return prompt

    @staticmethod
    def build_langchain_prompt_template(role: str = "Senior Engineer") -> ChatPromptTemplate:
        """
        Build a LangChain ChatPromptTemplate
        
        Args:
            role: The role context
            
        Returns:
            ChatPromptTemplate ready for LCEL
        """
        system_template = f"""You are an expert developer generating realistic digital artifacts.
Create authentic-looking code, configurations, and documentation that a {role} would write.
Ensure artifacts are realistic, consistent, and contextually appropriate."""

        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_template = "{user_input}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages([
            system_message_prompt,
            human_message_prompt
        ])

        return chat_prompt
