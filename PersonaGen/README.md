# PersonaGen - Artifact Persona Generator

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set API Key
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your-key-here"

# Linux/Mac
export GEMINI_API_KEY="your-key-here"
```

### 3. Generate Artifacts
```bash
python -m src.cli "Senior Python engineer"
```

## Usage Examples

### Basic Generation
```bash
# Generate 25 artifacts (default)
python -m src.cli "Backend engineer"

# Generate 50 artifacts
python -m src.cli "Backend engineer" --artifacts 50

# With custom database
python -m src.cli "DevOps engineer" --db my_db.db
```

### Advanced Options
```bash
# Custom categories
python -m src.cli "ML engineer" --categories code,config,docs

# Reproducible generation with seed
python -m src.cli "SRE" --seed 42

# Export to JSON
python -m src.cli "Frontend dev" --output artifacts.json

# Verbose output
python -m src.cli "Engineer" --verbose
```

## Testing

### Run Tests
```bash
# Test models
python tests/test_models.py

# Test PersonaBuilder
python tests/test_persona.py

# Test Persistence
python tests/test_persistence.py
```

## Project Structure

```
PersonaGen/
├── src/
│   ├── __init__.py
│   ├── models.py          # Pydantic data models
│   ├── persona.py         # Persona builder
│   ├── persistence.py     # SQLite database layer
│   ├── gemini_provider.py # LangChain Gemini wrapper
│   ├── prompts.py         # Prompt templates
│   ├── batcher.py         # Async batch generation
│   ├── postprocessor.py   # Validation pipeline
│   ├── cli.py             # CLI entry point
│   └── config.py          # Configuration
├── tests/
│   ├── test_models.py
│   ├── test_persona.py
│   └── test_persistence.py
├── data/                  # Data storage
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## API Key Setup

Get your free Google Gemini API key:
1. Visit https://ai.google.dev/
2. Click "Get API Key"
3. Create/select a project
4. Copy the key
5. Set environment variable: `GEMINI_API_KEY="your-key"`

## Database

Artifacts are stored in SQLite. Default: `artifacts.db`

Query the database:
```bash
sqlite3 artifacts.db
> SELECT DISTINCT persona_slug FROM artifacts;
> SELECT title, category FROM artifacts WHERE persona_slug='alice';
```

## Features

- ✓ Generate realistic personas from descriptions
- ✓ Create authentic-looking code, configs, docs
- ✓ LangChain + Gemini integration
- ✓ SQLite persistence
- ✓ Async batch processing
- ✓ Reproducible generation with seeds
- ✓ JSON export

## Development

### Add a new test
Create `tests/test_feature.py`:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_feature():
    # Your test here
    pass

if __name__ == "__main__":
    test_feature()
```

## License

Open source - modify as needed.
