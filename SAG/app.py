"""
REST API for the persona generator
Flask-based API with GET endpoints for generating personas and artifacts
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Tuple
from functools import wraps

from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest

from src.models import GenerationConfig
from src.persona import PersonaBuilder
from src.persistence import SQLiteDB
from src.gemini_provider import GeminiProvider
from src.batcher import BatchGenerator
from src.postprocessor import PostProcessor


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


# ============================================================================
# UTILITIES
# ============================================================================

def run_async(func):
    """Decorator to run async functions in Flask"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return func(*args, **kwargs)
        finally:
            loop.close()
    return wrapper


def parse_query_params() -> Dict[str, Any]:
    """Parse and validate query parameters"""
    return {
        'description': request.args.get('description', '').strip(),
        'artifacts': request.args.get('artifacts', 5, type=int),
        'db': request.args.get('db', 'artifacts.db'),
        'categories': request.args.get('categories', 'code,config,docs'),
        'model': request.args.get('model', 'gemini-3-flash-preview'),
        'temperature': request.args.get('temperature', 0.75, type=float),
        'seed': request.args.get('seed', None, type=int),
        'output': request.args.get('output', None),
        'verbose': request.args.get('verbose', 'false').lower() == 'true',
    }


def validate_params(params: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate request parameters"""
    if not params['description']:
        return False, "Missing required parameter: description"
    
    if params['artifacts'] < 1 or params['artifacts'] > 100:
        return False, "artifacts must be between 1 and 100"
    
    if params['temperature'] < 0.0 or params['temperature'] > 1.0:
        return False, "temperature must be between 0.0 and 1.0"
    
    return True, ""


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.route('/generate', methods=['GET'])
@run_async
async def generate_persona():
    """
    Generate a persona and its artifacts
    
    Query Parameters:
        - description (required): Persona description (e.g., 'Senior Python engineer')
        - artifacts (optional): Number of artifacts to generate (default: 5, max: 100)
        - db (optional): Database file path (default: artifacts.db)
        - categories (optional): Comma-separated artifact categories (default: code,config,docs)
        - model (optional): LLM model (default: gemini-3-flash-preview)
        - temperature (optional): Sampling temperature 0.0-1.0 (default: 0.75)
        - seed (optional): Random seed for reproducibility
        - output (optional): Output JSON file path
        - verbose (optional): Enable verbose output (true/false, default: false)
    
    Example:
        GET /generate?description=Senior%20Python%20engineer&artifacts=5&temperature=0.7
    """
    try:
        params = parse_query_params()
        
        # Validate parameters
        is_valid, error_msg = validate_params(params)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Parse categories
        categories = [c.strip() for c in params['categories'].split(",")]
        
        # Create configuration
        config = GenerationConfig(
            num_artifacts=params['artifacts'],
            temperature=params['temperature'],
            categories=categories,
            seed=params['seed'],
            model=params['model'],
        )
        
        if params['verbose']:
            print(f"[*] Building persona from: {params['description']}")
        
        # Build persona
        builder = PersonaBuilder()
        persona = builder.enrich(params['description'], seed=params['seed'])
        
        if params['verbose']:
            print(f"[+] Persona: {persona.name} ({persona.slug})")
            print(f"[+] Role: {persona.role}")
            print(f"[+] Company: {persona.company}")
        
        # Initialize provider and generator
        provider = GeminiProvider(model=params['model'])
        db = SQLiteDB(params['db'])
        batch_gen = BatchGenerator(db)
        postprocessor = PostProcessor(db)
        
        if params['verbose']:
            print(f"[*] Generating {params['artifacts']} artifacts...")
        
        # Generate batch
        artifacts = await batch_gen.generate_batch(persona, config, provider)
        
        if params['verbose']:
            print(f"[+] Generated {len(artifacts)} artifacts")
        
        # Post-process
        if params['verbose']:
            print(f"[*] Validating artifacts...")
        
        success, failed = postprocessor.process_batch(artifacts)
        
        if params['verbose']:
            print(f"[+] Persisted {success} artifacts ({failed} invalid)")
        
        # Export if requested
        if params['output']:
            with open(params['output'], "w") as f:
                json.dump([a.to_dict() for a in artifacts], f, indent=2)
            if params['verbose']:
                print(f"[+] Exported to {params['output']}")
        
        # Return response
        return jsonify({
            'success': success > 0,
            'persona': {
                'name': persona.name,
                'slug': persona.slug,
                'role': persona.role,
                'company': persona.company,
            },
            'artifacts': {
                'generated': len(artifacts),
                'persisted': success,
                'failed': failed,
            },
            'database': params['db'],
            'output_file': params['output'],
            'artifacts_list': [a.to_dict() for a in artifacts] if artifacts else [],
        }), 200
    
    except ValueError as e:
        error_msg = str(e)
        if "GEMINI_API_KEY" in error_msg:
            return jsonify({
                'error': error_msg,
                'setup': {
                    'instruction': 'Set your Gemini API key',
                    'windows': "$env:GEMINI_API_KEY='your-key-here'",
                    'linux_mac': "export GEMINI_API_KEY='your-key-here'",
                    'get_key': "https://ai.google.dev/"
                }
            }), 400
        else:
            return jsonify({'error': error_msg}), 400
    
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'type': type(e).__name__
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Persona Generator API',
    }), 200


@app.route('/info', methods=['GET'])
def info():
    """API information and available models"""
    return jsonify({
        'service': 'Persona Generator API',
        'version': '1.0',
        'endpoints': {
            'GET /generate': 'Generate a persona with artifacts',
            'GET /health': 'Health check',
            'GET /info': 'API information',
        },
        'parameters': {
            'description': {
                'type': 'string',
                'required': True,
                'example': 'Senior Python engineer',
                'description': 'Persona description'
            },
            'artifacts': {
                'type': 'integer',
                'default': 5,
                'min': 1,
                'max': 100,
                'description': 'Number of artifacts to generate'
            },
            'categories': {
                'type': 'string',
                'default': 'code,config,docs',
                'description': 'Comma-separated artifact categories'
            },
            'model': {
                'type': 'string',
                'default': 'gemini-3-flash-preview',
                'options': ['gemini-3-flash-preview', 'gemini-3-pro-preview', 'gemini-2.5-pro'],
                'description': 'LLM model to use'
            },
            'temperature': {
                'type': 'float',
                'default': 0.75,
                'min': 0.0,
                'max': 1.0,
                'description': 'Sampling temperature for randomness'
            },
            'seed': {
                'type': 'integer',
                'required': False,
                'description': 'Random seed for reproducibility'
            },
            'db': {
                'type': 'string',
                'default': 'artifacts.db',
                'description': 'Database file path'
            },
            'output': {
                'type': 'string',
                'required': False,
                'description': 'Optional output JSON file path'
            },
            'verbose': {
                'type': 'boolean',
                'default': False,
                'description': 'Enable verbose output'
            }
        },
        'examples': {
            'basic': '/generate?description=Senior%20Python%20engineer',
            'full': '/generate?description=DevOps%20Engineer&artifacts=10&temperature=0.8&model=gemini-3-pro-preview&seed=42&verbose=true',
            'categories': '/generate?description=Full%20Stack%20Developer&categories=code,docs,config'
        }
    }), 200


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request"""
    return jsonify({
        'error': 'Bad Request',
        'message': str(error.description)
    }), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': ['/generate', '/health', '/info']
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server Error"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': str(error)
    }), 500


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )