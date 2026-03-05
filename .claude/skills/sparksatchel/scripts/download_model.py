"""
Embedding Model Download Script

Download and setup embedding models for SparkSatchel.
Models will be downloaded to the project's data/cache/models directory.
"""

import os
import sys
from pathlib import Path


# Available models
MODELS = {
    "default": {
        "name": "paraphrase-multilingual-MiniLM-L12-v2",
        "size_mb": 470,
        "description": "Bilingual (Chinese/English), 50+ languages, balanced performance",
        "languages": ["Chinese", "English", "50+ others"],
        "dimension": 384
    },
    "chinese": {
        "name": "shibing624/text2vec-base-chinese",
        "size_mb": 110,
        "description": "Chinese-optimized, faster and more accurate for Chinese",
        "languages": ["Chinese"],
        "dimension": 768
    },
    "large": {
        "name": "intfloat/multilingual-e5-large",
        "size_mb": 1300,
        "description": "High accuracy multilingual, best for complex queries",
        "languages": ["100+ languages"],
        "dimension": 1024
    },
    "english": {
        "name": "all-MiniLM-L6-v2",
        "size_mb": 23,
        "description": "English only, ultra lightweight",
        "languages": ["English"],
        "dimension": 384
    }
}


def print_models():
    """Print available models"""
    print("\n📦 Available Embedding Models")
    print("=" * 60)
    for key, model in MODELS.items():
        print(f"\n[{key}] {model['name']}")
        print(f"    Size: {model['size_mb']}MB")
        print(f"    Languages: {', '.join(model['languages'])}")
        print(f"    Dimension: {model['dimension']}")
        print(f"    Description: {model['description']}")


def download_model(model_key: str = "default"):
    """Download specified model

    Args:
        model_key: Key from MODELS dict
    """
    if model_key not in MODELS:
        print(f"❌ Unknown model: {model_key}")
        print_models()
        sys.exit(1)

    model = MODELS[model_key]

    print(f"\n📥 Downloading model: {model['name']}")
    print(f"   Size: ~{model['size_mb']}MB")
    print(f"   This may take a few minutes...\n")

    try:
        from sentence_transformers import SentenceTransformer
        import torch

        # Check GPU availability
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cuda":
            print(f"🚀 Using GPU for faster inference")

        # Download model
        model_obj = SentenceTransformer(model['name'], device=device)

        # Get cache location
        cache_path = Path(model_obj._cache_dir) if hasattr(model_obj, '_cache_dir') else Path.home() / ".cache" / "huggingface"

        print(f"\n✅ Model downloaded successfully!")
        print(f"   Cache location: {cache_path}")
        print(f"   Dimension: {model_obj.get_sentence_embedding_dimension()}")

        # Test encoding
        test_text = "Hello, 世界!"
        embedding = model_obj.encode(test_text)
        print(f"   Test: Encoded '{test_text}' -> vector shape {embedding.shape}")

        print(f"\n💡 To use this model, modify src/models/embedding.py:")
        print(f"   DEFAULT_MODEL = \"{model['name']}\"")

    except ImportError:
        print("\n❌ sentence-transformers not installed")
        print("   Run: pip install sentence-transformers")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Download embedding models for SparkSatchel")
    parser.add_argument(
        "model",
        nargs="?",
        default="default",
        choices=list(MODELS.keys()),
        help="Model to download (default: default)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available models"
    )

    args = parser.parse_args()

    if args.list:
        print_models()
        sys.exit(0)

    download_model(args.model)


if __name__ == "__main__":
    main()
