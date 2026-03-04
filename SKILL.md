---
name: sparksatchel
description: Intelligent skill retrieval and recommendation system for Claude Code. Uses semantic search, intent analysis, and confidence scoring to recommend the most appropriate skills. Features: (1) Smart skill matching via bilingual embeddings (Chinese/English), (2) Prudent decision-making with three confidence tiers, (3) Historical learning from usage patterns, (4) Automatic health checking and lifecycle management, (5) Intelligent cache cleanup. Use when: User asks to find/recommend a skill, multiple skills might match a request, or skill selection requires intelligent analysis.
---

# SparkSatchel 灵犀妙计

A Meta-Skill that provides intelligent skill retrieval and recommendation for Claude Code.

## Core Philosophy

> "Think twice before acting, keep the user burden-free"

## Quick Start

```python
from src.retriever import SparkSatchel

sparksatchel = SparkSatchel()
result = sparksatchel.retrieve("process this PDF")
```

## Decision Mechanism

The system evaluates confidence and responds accordingly:

| Confidence Level | Threshold | Action |
|------------------|-----------|--------|
| **High** | >70% | Auto-recommend with reasoning |
| **Medium** | 40-70% | Recommend primary + alternatives |
| **Low** | <40% | Present candidates and ask user |

## Key Features

### 1. Semantic Retrieval

- **Bilingual embeddings**: Supports Chinese and English via paraphrase-multilingual-MiniLM-L12-v2
- **Sharded storage**: Skills organized by category for efficient retrieval
- **Vector similarity**: Matches user intent to skill descriptions

### 2. Intent Analysis

Extracts from user requests:
- Primary intent
- Keywords
- Entities (filenames, formats, etc.)

### 3. Historical Learning

- Tracks all skill calls
- Records success/failure feedback
- Calculates skill success rates
- Optimizes recommendation ranking

### 4. Health Checking

- Detects missing skills
- Identifies corrupted skills
- Handles version mismatches
- Provides fallback strategies

### 5. Cache Management

- Monitors database size
- Tracks record count
- Suggests cleanup when needed
- Supports auto/manual cleanup

## Usage Examples

### High Confidence (Auto-recommend)

```
User: "Process this PDF"
SparkSatchel: "I recommend pdf-skill because it specializes in PDF documents (92% historical success rate)"
```

### Medium Confidence (With alternatives)

```
User: "Create a document"
SparkSatchel: "I suggest docx-skill. pdf-skill is also available. Want me to compare them?"
```

### Low Confidence (Ask user)

```
User: "Process data"
SparkSatchel: "Found several matching skills. Which one fits best?
- xlsx-skill: Excel spreadsheet processing
- pandas-skill: Data analysis with Python
- csv-skill: CSV file handling"
```

## Builtin Models

SparkSatchel includes a lightweight bilingual embedding model for offline use:

- **Model**: paraphrase-multilingual-MiniLM-L12-v2
- **Size**: ~470MB
- **Languages**: 50+ including Chinese and English
- **First download**: Automatically downloaded on first use

### Optional: Use Better Models

For improved accuracy, you can install additional models:

```bash
# For better Chinese performance
pip install sentence-transformers
# Model: text2vec-base-chinese (110MB)

# For multilingual support
pip install sentence-transformers
# Model: intfloat/multilingual-e5-large (1.3GB)

# For API-based embedding (requires API key)
pip install openai
# Uses: text-embedding-3-small
```

To use a custom model, modify `src/models/embedding.py`:

```python
model = EmbeddingModel(
    model_name="text2vec-base-chinese",  # Your model
    device="cpu"  # or "cuda" for GPU
)
```

## Project Structure

```
SparkSatchel/
├── SKILL.md              # This file
├── requirements.txt      # Dependencies
├── src/
│   ├── retriever.py      # Main entry point
│   ├── models/           # Embedding models
│   ├── storage/          # Vector DB + history
│   ├── analysis/         # Intent + confidence
│   └── maintenance/      # Health + lifecycle + cache
└── data/                 # Data storage
    ├── collections/      # Vector databases
    └── history.db        # Call history
```

## API Reference

### Main Interface

```python
class SparkSatchel:
    def retrieve(self, user_request: str) -> RetrievalResult:
        """Search and recommend skills"""

    def feedback(self, skill_name: str, success: bool, feedback: str = ""):
        """Record user feedback"""

    def check_health(self) -> Dict:
        """Check system health"""

    def cleanup(self, strategy: dict = None):
        """Execute cache cleanup"""
```

### Retrieval Result

```python
@dataclass
class RetrievalResult:
    confidence: float              # 0-1
    recommended_skill: str         # Skill name
    reasoning: str                 # Explanation
    alternative_skills: List[str]  # For medium confidence
    candidate_skills: List[Dict]   # For low confidence
    requires_confirmation: bool    # Needs user input?
```

## Maintenance

### Check Health

```python
health = sparksatchel.check_health()
if health["cache"]["needs_cleanup"]:
    print(health["suggestion"])
```

### Cleanup Cache

```python
from src.maintenance.cache import CleanupStrategy

# By age (delete records older than 30 days)
sparksatchel.cleanup(CleanupStrategy.by_age(days=30))

# By count (keep recent 1000 records)
sparksatchel.cleanup(CleanupStrategy.by_count(keep=1000))
```

## Tech Stack

- **Python**: 3.10+
- **Vector DB**: ChromaDB
- **Embedding**: sentence-transformers
- **History**: SQLite

## Performance

| Metric | Target |
|--------|--------|
| Retrieval latency | <500ms (100k skills) |
| Memory usage | <500MB |
| Startup time | <3s |
| Accuracy | >85% |
