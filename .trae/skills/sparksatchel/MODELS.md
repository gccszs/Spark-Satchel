# Embedding Model Download Guide

This guide helps you download and configure different embedding models for SparkSatchel.

## Quick Download Commands

### Default Model (Already Downloaded ✅)
```bash
# paraphrase-multilingual-MiniLM-L12-v2 (470MB)
# Status: Pre-downloaded, ready to use
# Location: ~/.cache/huggingface/hub/
```

### Chinese-Optimized Model
```bash
pip install sentence-transformers
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('shibing624/text2vec-base-chinese')"
```

### High-Accuracy Multilingual Model
```bash
pip install sentence-transformers
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-large')"
```

### Ultra-Lightweight English Model
```bash
pip install sentence-transformers
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

## How to Switch Models

### Method 1: Edit Configuration (Permanent)

Edit `src/models/embedding.py`:
```python
class EmbeddingModel:
    DEFAULT_MODEL = "your-chosen-model-name"
```

### Method 2: Runtime Configuration (Temporary)

```python
from src.models.embedding import EmbeddingModel
from src.retriever import SparkSatchel

custom_model = EmbeddingModel(model_name="your-model")
sparksatchel = SparkSatchel(embedding_model=custom_model)
```

## Model Storage Location

Models are cached at:
- **Linux/Mac**: `~/.cache/huggingface/hub/`
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`

## GPU Acceleration

If you have NVIDIA GPU with CUDA:

```python
model = EmbeddingModel(
    model_name="paraphrase-multilingual-MiniLM-L12-v2",
    device="cuda"  # Use GPU instead of CPU
)
```

Performance improvement: 5-10x faster inference.
