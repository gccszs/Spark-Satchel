# SparkSatchel 灵犀妙计

<div align="center">

**智能技能检索与推荐系统**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

"心有灵犀一点通" - 理解用户意图，推荐最佳技能

</div>

---

## 🎯 简介

**SparkSatchel (灵犀妙计)** 是一个 Meta-Skill，专门为 Claude Code 设计的智能技能检索系统。它通过语义分析、意图推断和历史学习，帮助用户快速找到最合适的技能。

### 核心特点

✨ **三思而后行** - 根据置信度自动推荐或询问用户
🧠 **持续学习** - 记录使用历史，优化推荐准确性
🌏 **中英双语** - 基于 paraphrase-multilingual-MiniLM-L12-v2
🔧 **易于维护** - 智能缓存管理，自动健康检查

---

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/SparkSatchel.git
cd SparkSatchel

# 安装依赖
pip install -r requirements.txt
```

### 基本使用

```python
from src.retriever import SparkSatchel

# 初始化
sparksatchel = SparkSatchel()

# 检索技能
result = sparksatchel.retrieve("处理这个PDF")

# 高置信度 - 自动推荐
if result.confidence > 0.7:
    print(f"建议使用 {result.recommended_skill}")
    print(result.reasoning)

# 中置信度 - 提供备选
elif result.confidence > 0.4:
    print(f"建议使用 {result.recommended_skill}")
    print(f"备选：{result.alternative_skills}")

# 低置信度 - 询问用户
else:
    print("请从以下技能选择：")
    for skill in result.candidate_skills:
        print(f"  - {skill['skill_name']}: {skill['description']}")

# 记录反馈
sparksatchel.feedback(result.recommended_skill, success=True)
```

---

## 📊 决策机制

```
用户请求 → 意图推断 → 向量检索 → 置信度评估 → 决策
                                              ↓
                    ┌─────────────────────────────────┐
                    │           置信度                │
                    ├─────────────────────────────────┤
                    │ 高 (>70%)  │ 中 (40-70%) │ 低    │
                    ├─────────────────────────────────┤
                    │ 自动推荐   │ 推荐+备选   │ 询问  │
                    └─────────────────────────────────┘
```

---

## 🛠️ 功能详解

### 1. 智能检索

```python
# 自动索引技能目录
sparksatchel.index_skills()

# 按分类检索
result = sparksatchel.retrieve("创建文档", category="document")
```

### 2. 历史学习

```python
# 获取技能统计
stats = sparksatchel.history.get_skill_stats("pdf-skill")
print(f"成功率: {stats.success_rate:.0%}")
print(f"调用次数: {stats.total_calls}")
```

### 3. 健康检查

```python
# 检查系统健康
health = sparksatchel.check_health()

if health["cache"]["needs_cleanup"]:
    print("需要清理缓存")
    print(health["suggestion"])

if health["skills"]["unhealthy_count"] > 0:
    print("发现异常技能：")
    for skill in health["skills"]["unhealthy_list"]:
        print(f"  - {skill['skill']}: {skill['status']}")
```

### 4. 缓存管理

```python
from src.maintenance.cache import CleanupStrategy

# 按时间清理（删除30天前的记录）
sparksatchel.cleanup(CleanupStrategy.by_age(days=30))

# 按数量清理（保留最近1000条）
sparksatchel.cleanup(CleanupStrategy.by_count(keep=1000))

# 自动清理（如果需要）
sparksatchel.cache_manager.auto_cleanup_if_needed()
```

---

## 📁 项目结构

```
SparkSatchel/
├── SKILL.md              # Meta-skill 定义
├── README.md             # 本文档
├── DESIGN.md             # 设计文档
├── requirements.txt      # 依赖列表
│
├── src/                  # 源代码
│   ├── retriever.py      # 主入口
│   │
│   ├── models/           # 模型层
│   │   └── embedding.py  # Embedding 封装
│   │
│   ├── storage/          # 存储层
│   │   ├── vector_db.py  # ChromaDB 向量库
│   │   └── history.py    # SQLite 历史记录
│   │
│   ├── analysis/         # 分析层
│   │   ├── intent.py     # 意图推断
│   │   └── confidence.py # 置信度评估
│   │
│   └── maintenance/      # 维护模块
│       ├── health.py     # 健康检查
│       ├── lifecycle.py  # 生命周期管理
│       └── cache.py      # 缓存清理
│
└── data/                 # 数据目录
    ├── collections/      # 向量数据库（分库）
    ├── history.db        # 历史记录
    └── cache/            # 缓存目录
```

---

## 🔧 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 编程语言 | Python 3.10+ | 主要开发语言 |
| 向量数据库 | ChromaDB | 本地向量存储 |
| Embedding 模型 | sentence-transformers | 中英双语支持 |
| 历史记录 | SQLite | 轻量级数据库 |
| 向量计算 | NumPy | 高效数值计算 |

---

## 📈 性能指标

| 指标 | 目标 | 说明 |
|------|------|------|
| 检索延迟 | <500ms | 10万技能库 |
| 内存占用 | <500MB | 包含模型和向量库 |
| 启动时间 | <3s | 首次加载模型 |
| 推荐准确率 | >85% | 推荐技能符合用户意图 |

---

## 🎨 设计理念

### 灵犀 (Spark)

> "心有灵犀一点通"

- 理解用户意图的火花
- 语义相似度匹配
- 中英双语支持

### 妙计 (Satchel)

> "锦囊妙计，随需随取"

- 装满技能的锦囊
- 审慎决策机制
- 持续学习优化

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [ChromaDB](https://github.com/chroma-core/chroma) - 优秀的向量数据库
- [sentence-transformers](https://github.com/UKPLab/sentence-transformers) - 强大的文本 Embedding
- Claude Code 社区

---

<div align="center">

**让每一次技能调用都精准到位** ⚡

Made with ❤️ by SparkSatchel Team

</div>
