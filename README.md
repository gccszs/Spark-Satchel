<div align="center">

# SparkSatchel 灵犀妙计

**Intelligent Skill Retrieval & Recommendation System**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Embedding](https://img.shields.io/badge/Embedding-Bilingual-orange)](#embedding-models)

**"身无彩凤双飞翼，心有灵犀一点通"**

*"Without colorful phoenix wings to fly to you, our hearts connect at a single point."*

**SparkSatchel helps you and your Agent find the perfect SKILL from thousands, inferring the best match for your current task. A different kind of spark!**

[English](#english) | [中文](#中文)

</div>

---

## 中文 {#中文}

### 🎯 简介

**SparkSatchel (灵犀妙计)** 是一个 Meta-Skill，专为 Claude Code 设计的智能技能检索系统。它通过语义分析、意图推断和历史学习，帮助用户从海量技能中快速找到最合适的那个。

> "身无彩凤双飞翼，心有灵犀一点通"

在成千上万的技能中，灵犀妙计帮助你找到最适合当前任务的那一个。这，就是不一样的花火！

### ✨ 核心特点

- 🧠 **智能推断** - 理解用户意图，语义匹配技能
- ⚖️ **审慎决策** - 三思而后行，高置信度自动推荐，低置信度询问用户
- 📚 **持续学习** - 记录使用历史，优化推荐准确性
- 🌏 **中英双语** - 内置 50+ 语言支持，开袋即用
- 🔧 **易于维护** - 智能缓存管理，自动健康检查

### 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/gccszs/Spark-Satchel.git
cd Spark-Satchel

# 安装依赖
pip install -r requirements.txt
```

**✨ 开袋即用！** Embedding 模型已预下载 (~470MB)，无需等待。

```python
from src.retriever import SparkSatchel

# 初始化
sparksatchel = SparkSatchel()

# 检索技能
result = sparksatchel.retrieve("处理这个PDF")

# 根据置信度响应
if result.confidence > 0.7:
    print(f"建议使用 {result.recommended_skill}")
    print(result.reasoning)
elif result.confidence > 0.4:
    print(f"建议使用 {result.recommended_skill}")
    print(f"备选：{result.alternative_skills}")
else:
    print("请选择：")
    for skill in result.candidate_skills:
        print(f"  - {skill['skill_name']}")
```

### 📊 决策机制

```
高置信度 (>70%) → 自动推荐 + 说明理由
中置信度 (40-70%) → 推荐 + 备选方案
低置信度 (<40%) → 展示候选 + 询问用户
```

### 🛠️ 功能详解

| 功能 | 说明 |
|------|------|
| **语义检索** | 基于 embedding 的向量相似度搜索 |
| **意图推断** | 提取用户请求的核心意图和关键词 |
| **置信度评估** | 多维度综合评分：相似度、历史、相关性 |
| **历史学习** | 追踪调用成功率，动态优化排序 |
| **健康检查** | 检测技能状态，提供降级策略 |
| **缓存管理** | 智能清理策略，释放存储空间 |

### 📁 项目结构

```
SparkSatchel/
├── SKILL.md       # Meta-skill 定义
├── README.md      # 本文档
├── MODELS.md      # 模型选择指南
├── requirements.txt
└── src/
    ├── retriever.py      # 主入口
    ├── models/           # Embedding 封装
    ├── storage/          # 向量库 + 历史
    ├── analysis/         # 意图 + 置信度
    └── maintenance/      # 健康 + 生命周期 + 缓存
```

### 🔧 技术栈

- **Python** 3.10+
- **ChromaDB** - 向量数据库
- **sentence-transformers** - Embedding 模型
- **SQLite** - 历史记录

### 📖 文档

- [设计文档](DESIGN.md) - 完整的系统设计说明
- [模型指南](MODELS.md) - Embedding 模型选择和下载
- [SKILL.md](SKILL.md) - Meta-skill 定义

### 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

### 📄 许可证

[MIT License](LICENSE)

---

<div align="center">

**让每一次技能调用都精准到位** ⚡

Made with ❤️ by [SparkSatchel Team](https://github.com/gccszs/Spark-Satchel)

</div>

---

## English {#english}

### 🎯 Overview

**SparkSatchel** is a Meta-Skill designed for Claude Code that provides intelligent skill retrieval and recommendation. Through semantic analysis, intent inference, and historical learning, it helps users quickly find the most suitable skill from thousands.

> "身无彩凤双飞翼，心有灵犀一点通"

From thousands of skills, SparkSatchel infers the perfect match for your current task. A different kind of spark!

### ✨ Key Features

- 🧠 **Smart Inference** - Understands user intent, semantically matches skills
- ⚖️ **Prudent Decision** - Thinks before acting: auto-recommends with high confidence, asks user with low confidence
- 📚 **Continuous Learning** - Tracks usage history, optimizes recommendations
- 🌏 **Bilingual Support** - Built-in 50+ languages, ready to use out of the box
- 🔧 **Easy Maintenance** - Smart cache management, automatic health checks

### 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/gccszs/Spark-Satchel.git
cd Spark-Satchel

# Install dependencies
pip install -r requirements.txt
```

**✨ Ready to use!** The embedding model is pre-downloaded (~470MB), no waiting required.

```python
from src.retriever import SparkSatchel

# Initialize
sparksatchel = SparkSatchel()

# Retrieve skills
result = sparksatchel.retrieve("process this PDF")

# Respond based on confidence
if result.confidence > 0.7:
    print(f"Recommend: {result.recommended_skill}")
    print(result.reasoning)
elif result.confidence > 0.4:
    print(f"Recommend: {result.recommended_skill}")
    print(f"Alternatives: {result.alternative_skills}")
else:
    print("Please select:")
    for skill in result.candidate_skills:
        print(f"  - {skill['skill_name']}")
```

### 📊 Decision Mechanism

```
High Confidence (>70%)   → Auto-recommend with reasoning
Medium Confidence (40-70%) → Recommend + alternatives
Low Confidence (<40%)     → Present candidates + ask user
```

### 🛠️ Features

| Feature | Description |
|---------|-------------|
| **Semantic Search** | Vector similarity search based on embeddings |
| **Intent Analysis** | Extracts core intent and keywords from requests |
| **Confidence Evaluation** | Multi-dimensional scoring: similarity, history, relevance |
| **Historical Learning** | Tracks success rates, dynamically optimizes ranking |
| **Health Checking** | Detects skill status, provides fallback strategies |
| **Cache Management** | Smart cleanup strategies, frees storage space |

### 📁 Project Structure

```
SparkSatchel/
├── SKILL.md       # Meta-skill definition
├── README.md      # This file
├── MODELS.md      # Model selection guide
├── requirements.txt
└── src/
    ├── retriever.py      # Main entry point
    ├── models/           # Embedding wrapper
    ├── storage/          # Vector DB + history
    ├── analysis/         # Intent + confidence
    └── maintenance/      # Health + lifecycle + cache
```

### 🔧 Tech Stack

- **Python** 3.10+
- **ChromaDB** - Vector database
- **sentence-transformers** - Embedding models
- **SQLite** - History tracking

### 📖 Documentation

- [Design Doc](DESIGN.md) - Complete system design
- [Model Guide](MODELS.md) - Embedding model selection and download
- [SKILL.md](SKILL.md) - Meta-skill definition

### 🤝 Contributing

Contributions, issues, and feature requests are welcome!

### 📄 License

[MIT License](LICENSE)

---

<div align="center">

**Making every skill call precise** ⚡

Made with ❤️ by [SparkSatchel Team](https://github.com/gccszs/Spark-Satchel)

</div>
