"""
Command-line interface for the persona generator
"""

import argparse
import asyncio
import json
from pathlib import Path
from .models import GenerationConfig
from .persona import PersonaBuilder
from .persistence import SQLiteDB
from .gemini_provider import GeminiProvider
from .batcher import BatchGenerator
from .postprocessor import PostProcessor


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate realistic digital personas and artifacts"
    )
    
    parser.add_argument(
        "description",
        help="Persona description (e.g., 'Senior Python engineer')"
    )
    
    parser.add_argument(
        "--artifacts",
        type=int,
        default=5,
        help="Number of artifacts to generate (default: 5)"
    )
    
    parser.add_argument(
        "--db",
        default="artifacts.db",
        help="Database file path (default: artifacts.db)"
    )
    
    parser.add_argument(
        "--categories",
        default="code,config,docs",
        help="Artifact categories (default: code,config,docs)"
    )

    parser.add_argument(
        "--model",
        default="gemini-3-flash-preview",
        help="LLM model to use (default: gemini-3-flash-preview). Try: gemini-3-pro-preview, gemini-2.5-pro"
    )
    
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.75,
        help="Sampling temperature (0.0-1.0, default: 0.75)"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducibility"
    )
    
    parser.add_argument(
        "--output",
        help="Output JSON file (optional)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()

    # Parse categories
    categories = [c.strip() for c in args.categories.split(",")]

    # Create configuration
    config = GenerationConfig(
        num_artifacts=args.artifacts,
        temperature=args.temperature,
        categories=categories,
        seed=args.seed,
        model=args.model,
    )

    # Build persona
    if args.verbose:
        print(f"[*] Building persona from: {args.description}")
    
    builder = PersonaBuilder()
    persona = builder.enrich(args.description, seed=args.seed)
    
    if args.verbose:
        print(f"[+] Persona: {persona.name} ({persona.slug})")
        print(f"[+] Role: {persona.role}")
        print(f"[+] Company: {persona.company}")

    # Try to generate artifacts
    try:
        # Initialize provider and generator
        provider = GeminiProvider(model=args.model)
        db = SQLiteDB(args.db)
        batch_gen = BatchGenerator(db)
        postprocessor = PostProcessor(db)

        if args.verbose:
            print(f"[*] Generating {args.artifacts} artifacts...")

        # Generate batch
        async def generate():
            return await batch_gen.generate_batch(persona, config, provider)

        artifacts = asyncio.run(generate())

        if args.verbose:
            print(f"[+] Generated {len(artifacts)} artifacts")

        # Post-process
        if args.verbose:
            print(f"[*] Validating artifacts...")
        
        success, failed = postprocessor.process_batch(artifacts)
        
        if args.verbose:
            print(f"[+] Persisted {success} artifacts ({failed} invalid)")

        # Export if requested
        if args.output:
            with open(args.output, "w") as f:
                json.dump([a.to_dict() for a in artifacts], f, indent=2)
            if args.verbose:
                print(f"[+] Exported to {args.output}")

        # Check if any artifacts were actually generated
        if success > 0:
            print(f"\n[SUCCESS] Successfully generated persona: {persona.name}")
            print(f"  Database: {args.db}")
            print(f"  Artifacts: {success}")
        else:
            print(f"\n[WARNING] Persona created but no artifacts generated")
            print(f"  Persona: {persona.name}")
            print(f"  Database: {args.db}")
            print(f"  Artifacts: {success}")
            print("\n  The model may not be available. Try using a different model with --model flag")
            print("  Example: python -m src.cli 'Engineer' --model gemini-pro")

    except ValueError as e:
        if "GEMINI_API_KEY" in str(e):
            print(f"\n[ERROR] {e}")
            print("\n  To generate artifacts, set your API key:")
            print("  $env:GEMINI_API_KEY='your-key-here'  # Windows PowerShell")
            print("  export GEMINI_API_KEY='your-key-here'  # Linux/Mac")
            print("\n  Get your key from: https://ai.google.dev/")
        else:
            print(f"\n[ERROR] {e}")


if __name__ == "__main__":
    main()
