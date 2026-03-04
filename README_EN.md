<div align="center">

# 🧠 SparkSatchel

**Intelligent Skill Retrieval & Recommendation System**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Embedding](https://img.shields.io/badge/Embedding-50%2B%20Languages-orange)](#embedding-models)

**English** | [中文](./README.md)

---

**"身无彩凤双飞翼，心有灵犀一点通"**

*Without colorful phoenix wings to fly to you, our hearts connect at a single point.*

SparkSatchel helps you and your Agent find the perfect SKILL from thousands by inferring the best match for your current task.

A different kind of spark! ⚡

---

*Compatible with Claude Code, Cursor, Windsurf, Trae, and all AI IDEs*

</div>

---

## 📖 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Decision Mechanism](#decision-mechanism)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**SparkSatchel** is an intelligent skill retrieval and recommendation system designed for all AI IDEs (Claude Code, Cursor, Windsurf, Trae, etc.).

Through semantic analysis, intent inference, and historical learning, it helps users quickly find the most suitable skill from thousands.

### Why SparkSatchel?

As the AI skill ecosystem grows, users may install hundreds of skills. When completing a task:

```
❌ Traditional: Manually search skill names, read descriptions one by one
✅ SparkSatchel: Describe your need, automatically get the best skill recommendation
```

---

## ✨ Key Features

### 🧠 Smart Inference

- Understands natural language descriptions of user intent
- Semantic similarity matching based on embeddings
- Supports 50+ languages with bilingual optimization (Chinese/English)

### ⚖️ Prudent Decision

Responds intelligently based on confidence:

| Confidence | Action | Example |
|------------|--------|---------|
| **High (>70%)** | Auto-recommend with reasoning | "Use pdf-skill, 92% success rate" |
| **Medium (40-70%)** | Recommend + alternatives | "Use docx-skill, alternative: pdf-skill" |
| **Low (<40%)** | Present candidates + ask user | "Choose: xlsx-skill, pandas-skill..." |

### 📚 Continuous Learning

- Tracks every skill call
- Records success/failure feedback
- Calculates skill success rates
- Dynamically optimizes recommendation ranking

### 🔧 Easy Maintenance

- Automatic health checks (monitors skill status)
- Smart cache cleanup (frees storage space)
- Lifecycle management (version migration, fallback strategies)

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/gccszs/Spark-Satchel.git
cd Spark-Satchel

# Install dependencies
pip install -r requirements.txt
```

### ✨ Ready to Use

**Great news!** The embedding model is pre-downloaded (~470MB), no waiting required:

- ✅ **Pre-installed**: paraphrase-multilingual-MiniLM-L12-v2
- ✅ **Bilingual**: Supports 50+ languages
- ✅ **Offline**: No internet connection needed
- ✅ **Plug & Play**: Use immediately after installing dependencies

### Basic Usage

```python
from src.retriever import SparkSatchel

# Initialize (model pre-installed)
sparksatchel = SparkSatchel()

# Retrieve skills
result = sparksatchel.retrieve("process this PDF")

# Respond based on confidence
if result.confidence > 0.7:
    # High confidence - direct recommendation
    print(f"✅ Recommend: {result.recommended_skill}")
    print(result.reasoning)

elif result.confidence > 0.4:
    # Medium confidence - provide alternatives
    print(f"💡 Recommend: {result.recommended_skill}")
    print(f"Alternatives: {', '.join(result.alternative_skills)}")

else:
    # Low confidence - ask user
    print("❓ Please choose from:")
    for skill in result.candidate_skills:
        print(f"  - {skill['skill_name']}: {skill['description']}")

# Record feedback (helps system learn)
sparksatchel.feedback(result.recommended_skill, success=True)
```

---

## 📊 Decision Mechanism

```
User Request → Intent Analysis → Vector Search → Confidence → Decision
                                                          ↓
                                    ┌─────────────────────────────────┐
                                    │           Confidence              │
                                    ├─────────────────────────────────┤
                                    │ High (>70%)  │ Med (40-70%) │ Low│
                                    ├─────────────────────────────────┤
                                    │ Auto-rec     │ Rec+Alt    │ Ask│
                                    └─────────────────────────────────┘
```

### Usage Examples

**Example 1: High Confidence**
```
User: "Process this PDF"
SparkSatchel: "I recommend pdf-skill because it specializes in PDF documents (92% historical success rate)"
```

**Example 2: Medium Confidence**
```
User: "Create a document"
SparkSatchel: "I suggest docx-skill. pdf-skill is also available. Want me to compare?"
```

**Example 3: Low Confidence**
```
User: "Process data"
SparkSatchel: "Found 3 matching skills:
  - xlsx-skill: Excel spreadsheet processing
  - pandas-skill: Python data analysis
  - csv-skill: CSV file handling
Please choose the most suitable one."
```

---

## 🛠️ Features

### 1. Semantic Retrieval

| Feature | Description |
|---------|-------------|
| **Sharded Storage** | Skills organized by category for efficient retrieval |
| **Vector Similarity** | Semantic matching based on embeddings |
| **Bilingual** | Default model supports 50+ languages |

### 2. Intent Analysis

Extracts from user requests:
- Primary intent (e.g., document processing, project creation)
- Keywords (e.g., PDF, Word, Excel)
- Entities (e.g., filenames, formats)

### 3. Confidence Evaluation

Multi-dimensional scoring:
- **Similarity** (50%): Semantic matching degree
- **History** (30%): Success rate and call count
- **Relevance** (15%): Keyword matching
- **Freshness** (5%): Recent usage bonus

### 4. Historical Learning

```python
# Get skill statistics
stats = sparksatchel.history.get_skill_stats("pdf-skill")
print(f"Success rate: {stats.success_rate:.0%}")
print(f"Total calls: {stats.total_calls}")
print(f"Last called: {stats.last_called}")
```

### 5. Health Checking

```python
# Check system health
health = sparksatchel.check_health()

if health["cache"]["needs_cleanup"]:
    print(f"⚠️ {health['suggestion']}")

if health["skills"]["unhealthy_count"] > 0:
    print(f"⚠️ Found {health['skills']['unhealthy_count']} unhealthy skills")
```

### 6. Cache Management

```python
from src.maintenance.cache import CleanupStrategy

# Cleanup by age (delete records older than 30 days)
sparksatchel.cleanup(CleanupStrategy.by_age(days=30))

# Cleanup by count (keep recent 1000 records)
sparksatchel.cleanup(CleanupStrategy.by_count(keep=1000))

# Auto cleanup (if needed)
sparksatchel.cache_manager.auto_cleanup_if_needed()
```

---

## 🔧 Tech Stack

| Component | Technology | Description |
|-----------|------------|-------------|
| Language | Python 3.10+ | Main development language |
| Vector DB | ChromaDB | Local vector storage |
| Embedding | sentence-transformers | Bilingual support |
| History | SQLite | Lightweight database |
| Vector Math | NumPy | Efficient numerical computation |

### Project Structure

```
SparkSatchel/
├── SKILL.md               # Meta-skill definition
├── README.md              # Chinese documentation
├── README_EN.md           # This file (English)
├── DESIGN.md              # Design document
├── MODELS.md              # Model selection guide
├── GITHUB_DESCRIPTION.md  # Repository description
├── requirements.txt       # Dependencies
│
├── scripts/               # Utility scripts
│   └── download_model.py  # Model download script
│
├── src/                   # Source code
│   ├── retriever.py       # Main entry point
│   ├── models/            # Embedding wrapper
│   ├── storage/           # Vector DB + history
│   ├── analysis/          # Intent + confidence
│   └── maintenance/       # Health + lifecycle + cache
│
└── data/                  # Data directory
    ├── collections/       # Vector databases (sharded)
    ├── history.db         # Call history
    └── cache/             # Cache directory
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [DESIGN.md](DESIGN.md) | Complete system design document |
| [MODELS.md](MODELS.md) | Embedding model selection and download guide |
| [SKILL.md](SKILL.md) | Meta-skill definition |

---

## 🎨 Design Philosophy

### Spark (灵犀)

> "身无彩凤双飞翼，心有灵犀一点通"

- Spark of understanding user intent
- Semantic similarity matching
- Bilingual support

### Satchel (妙计)

> "锦囊妙计，随需随取"

- Bag full of skills
- Prudent decision mechanism
- Continuous learning optimization

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- [ChromaDB](https://github.com/chroma-core/chroma) - Excellent vector database
- [sentence-transformers](https://github.com/UKPLab/sentence-transformers) - Powerful text embeddings
- All contributors and users

---

<div align="center">

**Making every skill call precise** ⚡

Compatible with Claude Code, Cursor, Windsurf, Trae, and all AI IDEs

Made with ❤️ by [SparkSatchel Team](https://github.com/gccszs/Spark-Satchel)

</div>
