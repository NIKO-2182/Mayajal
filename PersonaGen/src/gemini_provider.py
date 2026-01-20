"""
Google Gemini provider with LangChain integration
"""

import os
import json
from typing import List, Optional, Dict
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from .models import Artifact, GenerationConfig

# Load .env file from src directory
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Also try loading from parent directory (PersonaGen/)
parent_env_path = Path(__file__).parent.parent / ".env"
if parent_env_path.exists():
    load_dotenv(parent_env_path)


class GeminiProvider:
    """LangChain wrapper for Google Gemini API"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-3-flash-preview"):
        """
        Initialize Gemini provider
        
        Args:
            api_key: Google API key (or use GEMINI_API_KEY env var or .env file)
            model: Model name (default: gemini-3-flash-preview)
        """
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not set. Please either:\n"
                "  1. Set environment variable: $env:GEMINI_API_KEY='your-key'\n"
                "  2. Create .env file in src/ or PersonaGen/ directory with: GEMINI_API_KEY=your-key\n"
                "  3. Pass api_key parameter directly\n"
                "Get your key from: https://ai.google.dev/"
            )

        self.api_key = api_key
        self.model = model
        self._init_model()

    def _init_model(self):
        """Initialize LangChain ChatGoogleGenerativeAI"""
        self.llm = ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=self.api_key,
            temperature=0.75,
        )

    def generate_artifacts(
        self,
        prompt: str,
        num_artifacts: int = 25,
        temperature: float = 0.75,
        max_tokens: int = 2000,
    ) -> List[Dict]:
        """
        Generate artifacts using Gemini
        
        Args:
            prompt: Full prompt with persona context
            num_artifacts: Number of artifacts to generate
            temperature: Sampling temperature
            max_tokens: Max tokens per response
            
        Returns:
            List of generated artifact dictionaries
        """
        try:
            # Create the LLM with specific temperature
            llm = ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=self.api_key,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

            # Call the model
            response = llm.invoke([HumanMessage(content=prompt)])
            
            # Parse response
            content = response.content
            artifacts = self._parse_artifacts(content, num_artifacts)
            
            return artifacts
        except Exception as e:
            print(f"Error generating artifacts: {e}")
            return []

    def _parse_artifacts(self, content: str, num_artifacts: int) -> List[Dict]:
        """
        Parse JSON artifacts from model response
        
        Args:
            content: Model response content (may contain unescaped newlines or be a LangChain message object)
            num_artifacts: Expected number of artifacts
            
        Returns:
            List of artifact dictionaries
        """
        import re
        
        artifacts = []
        
        # Convert content to string if needed (handle LangChain message objects)
        if isinstance(content, list) and len(content) > 0:
            # Handle LangChain response format: [{'type': 'text', 'text': '...'}]
            if isinstance(content[0], dict) and 'text' in content[0]:
                content = content[0]['text']
        
        if not isinstance(content, str):
            content = str(content)
        
        try:
            # Find the JSON array in the response
            if "[" not in content or "]" not in content:
                print(f"DEBUG: No JSON array found in response. First 100 chars: {content[:100]}")
                return artifacts
            
            # Extract from first [ to last ]
            start_idx = content.find("[")
            end_idx = content.rfind("]") + 1
            json_str = content[start_idx:end_idx]
            
            # Try direct parsing first
            try:
                data = json.loads(json_str)
                if isinstance(data, list):
                    artifacts = data[:num_artifacts]
                    return artifacts
            except json.JSONDecodeError:
                pass
            
            # Parse JSON array by finding individual objects while respecting brace nesting
            print("DEBUG: Using brace-matching artifact extraction")
            
            artifacts_raw = []
            depth = 0
            current_obj = []
            in_string = False
            escape_next = False
            
            for char in json_str:
                if escape_next:
                    current_obj.append(char)
                    escape_next = False
                    continue
                
                if char == '\\' and in_string:
                    current_obj.append(char)
                    escape_next = True
                    continue
                
                if char == '"':
                    in_string = not in_string
                    current_obj.append(char)
                    continue
                
                if not in_string:
                    if char == '{':
                        if depth == 0:
                            current_obj = []  # Start new object
                        depth += 1
                        current_obj.append(char)
                    elif char == '}':
                        depth -= 1
                        current_obj.append(char)
                        if depth == 0 and current_obj:
                            artifacts_raw.append(''.join(current_obj))
                            current_obj = []
                    else:
                        if depth > 0:
                            current_obj.append(char)
                else:
                    current_obj.append(char)
            
            # Process each extracted object
            for obj_str in artifacts_raw:
                if len(artifacts) >= num_artifacts:
                    break
                
                # Try to fix and parse as JSON first
                try:
                    # Fix unescaped newlines within strings
                    def fix_json_string(s):
                        result = []
                        in_string = False
                        escape_next = False
                        for char in s:
                            if escape_next:
                                result.append(char)
                                escape_next = False
                            elif char == '\\':
                                result.append(char)
                                escape_next = True
                            elif char == '"':
                                result.append(char)
                                in_string = not in_string
                            elif char in '\n\r\t' and in_string:
                                # Escape literal whitespace in strings
                                if char == '\n':
                                    result.append('\\n')
                                elif char == '\r':
                                    result.append('\\r')
                                elif char == '\t':
                                    result.append('\\t')
                            else:
                                result.append(char)
                        return ''.join(result)
                    
                    fixed_obj = fix_json_string(obj_str)
                    obj_data = json.loads(fixed_obj)
                    
                    if 'title' in obj_data and 'category' in obj_data and 'content' in obj_data:
                        artifacts.append({
                            "title": obj_data.get('title', ''),
                            "category": obj_data.get('category', ''),
                            "file_extension": obj_data.get('file_extension', ''),
                            "content": obj_data.get('content', '')
                        })
                    continue
                except json.JSONDecodeError:
                    pass
                
                # Fallback: manual field extraction using regex
                try:
                    title_match = re.search(r'"title"\s*:\s*"([^"]*(?:\\"[^"]*)*)"', obj_str)
                    category_match = re.search(r'"category"\s*:\s*"([^"]*)"', obj_str)
                    ext_match = re.search(r'"file_extension"\s*:\s*"([^"]*)"', obj_str)
                    content_match = re.search(r'"content"\s*:\s*"((?:[^"\\]|\\.|\n|\r|\t)*?)"(?:\s*[,}])', obj_str)
                    
                    if title_match and category_match and content_match:
                        content_text = content_match.group(1)
                        # Unescape
                        content_text = content_text.replace('\\n', '\n')
                        content_text = content_text.replace('\\t', '\t')
                        content_text = content_text.replace('\\r', '\r')
                        content_text = content_text.replace('\\"', '"')
                        content_text = content_text.replace('\\\\', '\\')
                        
                        artifacts.append({
                            "title": title_match.group(1),
                            "category": category_match.group(1),
                            "file_extension": ext_match.group(1) if ext_match else '',
                            "content": content_text
                        })
                except:
                    pass
            
            if artifacts:
                print(f"DEBUG: Successfully extracted {len(artifacts)} artifacts")
                return artifacts
                
        except Exception as e:
            print(f"Failed to parse JSON from response: {e}")
            print(f"DEBUG: Response content (first 300 chars): {content[:300]}")
        
        return artifacts
