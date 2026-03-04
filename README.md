<div align="center">

# 🧠 SparkSatchel 灵犀妙计

**智能技能检索与推荐系统**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Embedding](https://img.shields.io/badge/Embedding-50%2B%20Languages-orange)](#embedding-模型)

[English](./README_EN.md) | **中文**

• • •

**"身无彩凤双飞翼，心有灵犀一点通"**

灵犀妙计帮助你和你的 Agent 从万千技能中推断出你最适合当前任务的技能。

不一样的花火！⚡

• • •

*适用于 Claude Code、Cursor、Windsurf、Trae 等所有 AI IDE*

</div>

---

## 📖 目录

- [简介](#-简介)
- [快速开始](#-快速开始)
- [核心特点](#-核心特点)
- [决策机制](#-决策机制)
- [功能详解](#-功能详解)
- [技术架构](#-技术架构)
- [文档](#-文档)
- [贡献](#-贡献)

---

## 🎯 简介

**SparkSatchel (灵犀妙计)** 是一个智能技能检索与推荐系统，适用于所有 AI IDE（Claude Code、Cursor、Windsurf、Trae 等）。

它通过语义分析、意图推断和历史学习，帮助用户从海量技能中快速找到最合适的那个。

### 为什么需要灵犀妙计？

随着 AI 技能生态系统的发展，用户可能会安装数百个技能。当需要完成某个任务时：

```
❌ 传统方式：手动搜索技能名称，逐个查看描述
✅ 灵犀妙计：描述你的需求，自动推荐最合适的技能
```

---

## 🚀 快速开始

### 方式一：npx 安装（推荐）

```bash
# 使用 npx 快速安装
npx sparksatchel

# 安装完成后直接使用
python -c "from src.retriever import SparkSatchel; s = SparkSatchel(); print(s.retrieve('处理PDF').reasoning)"
```

### 方式二：Git 克隆

```bash
# 克隆仓库
git clone https://github.com/gccszs/Spark-Satchel.git
cd Spark-Satchel

# 安装依赖
pip install -r requirements.txt
```

### ✨ 开袋即用

**好消息！** Embedding 模型已预下载 (~470MB)，无需等待：

- ✅ **预装模型**: paraphrase-multilingual-MiniLM-L12-v2
- ✅ **中英双语**: 支持 50+ 语言
- ✅ **离线可用**: 无需联网
- ✅ **即装即用**: 安装依赖后立即使用

### 基本使用

```python
from src.retriever import SparkSatchel

# 初始化（模型已预装）
sparksatchel = SparkSatchel()

# 检索技能
result = sparksatchel.retrieve("处理这个PDF")

# 根据置信度响应
if result.confidence > 0.7:
    # 高置信度 - 直接推荐
    print(f"✅ 建议使用 {result.recommended_skill}")
    print(result.reasoning)

elif result.confidence > 0.4:
    # 中置信度 - 提供备选
    print(f"💡 建议使用 {result.recommended_skill}")
    print(f"备选：{', '.join(result.alternative_skills)}")

else:
    # 低置信度 - 询问用户
    print("❓ 请从以下技能中选择：")
    for skill in result.candidate_skills:
        print(f"  - {skill['skill_name']}: {skill['description']}")

# 记录反馈（帮助系统学习）
sparksatchel.feedback(result.recommended_skill, success=True)
```

---

## ✨ 核心特点

### 🧠 智能推断

- 理解用户意图的自然语言描述
- 基于 embedding 的语义相似度匹配
- 支持 50+ 语言，中英双语优化

### ⚖️ 审慎决策

根据置信度智能响应：

| 置信度 | 行为 | 示例 |
|--------|------|------|
| **高 (>70%)** | 自动推荐 + 说明理由 | "建议用 pdf-skill，成功率 92%" |
| **中 (40-70%)** | 推荐 + 备选方案 | "建议用 docx-skill，备选：pdf-skill" |
| **低 (<40%)** | 展示候选 + 询问用户 | "请选择：xlsx-skill、pandas-skill..." |

### 📚 持续学习

- 记录每次技能调用
- 追踪成功/失败反馈
- 计算技能成功率
- 动态优化推荐排序

### 🔧 易于维护

- 自动健康检查（检测技能状态）
- 智能缓存清理（释放存储空间）
- 生命周期管理（版本迁移、降级策略）

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

### 使用示例

**示例 1：高置信度**

```
用户: "处理这个PDF"
灵犀妙计: "建议用 pdf-skill，因为它专门处理 PDF 文档（历史成功率 92%）"
```

**示例 2：中置信度**

```
用户: "创建文档"
灵犀妙计: "建议用 docx-skill。pdf-skill 也可以，要我详细对比吗？"
```

**示例 3：低置信度**

```
用户: "处理数据"
灵犀妙计: "找到 3 个可能符合的技能：
  - xlsx-skill: Excel 电子表格处理
  - pandas-skill: Python 数据分析
  - csv-skill: CSV 文件处理
请选择最合适的一个。"
```

---

## 🛠️ 功能详解

### 1. 语义检索

| 特性 | 说明 |
|------|------|
| **分库存储** | 技能按类别分库，提升检索效率 |
| **向量相似度** | 基于 embedding 的语义匹配 |
| **中英双语** | 默认模型支持 50+ 语言 |

### 2. 意图推断

从用户请求中提取：
- 主要意图（如：文档处理、项目创建）
- 关键词（如：PDF、Word、Excel）
- 实体（如：文件名、格式）

### 3. 置信度评估

多维度综合评分：
- **相似度** (50%): 语义匹配程度
- **历史表现** (30%): 成功率和调用次数
- **相关性** (15%): 关键词匹配
- **新鲜度** (5%): 最近使用加成

### 4. 历史学习

```python
# 获取技能统计
stats = sparksatchel.history.get_skill_stats("pdf-skill")
print(f"成功率: {stats.success_rate:.0%}")
print(f"调用次数: {stats.total_calls}")
print(f"最后调用: {stats.last_called}")
```

### 5. 健康检查

```python
# 检查系统健康
health = sparksatchel.check_health()

if health["cache"]["needs_cleanup"]:
    print(f"⚠️ {health['suggestion']}")

if health["skills"]["unhealthy_count"] > 0:
    print(f"⚠️ 发现 {health['skills']['unhealthy_count']} 个异常技能")
```

### 6. 缓存管理

```python
from src.maintenance.cache import CleanupStrategy

# 按时间清理（删除 30 天前的记录）
sparksatchel.cleanup(CleanupStrategy.by_age(days=30))

# 按数量清理（保留最近 1000 条）
sparksatchel.cleanup(CleanupStrategy.by_count(keep=1000))

# 自动清理（如果需要）
sparksatchel.cache_manager.auto_cleanup_if_needed()
```

---

## 🔧 技术架构

### 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 编程语言 | Python 3.10+ | 主要开发语言 |
| 向量数据库 | ChromaDB | 本地向量存储 |
| Embedding | sentence-transformers | 中英双语支持 |
| 历史记录 | SQLite | 轻量级数据库 |
| 向量计算 | NumPy | 高效数值计算 |

### 项目结构

```
SparkSatchel/
├── SKILL.md               # Meta-skill 定义
├── README.md              # 本文档（中文）
├── README_EN.md           # 英文文档
├── MODELS.md              # 模型选择指南
├── requirements.txt       # 依赖列表
├── package.json           # npx 配置
│
├── scripts/               # 工具脚本
│   └── download_model.py  # 模型下载脚本
│
├── src/                   # 源代码
│   ├── retriever.py       # 主入口
│   ├── models/            # Embedding 封装
│   ├── storage/           # 向量库 + 历史
│   ├── analysis/          # 意图 + 置信度
│   └── maintenance/       # 健康 + 生命周期 + 缓存
│
└── data/                  # 数据目录
    ├── collections/       # 向量数据库（分库）
    ├── history.db         # 历史记录
    └── cache/             # 缓存目录
```

---

## 📚 文档

| 文档 | 描述 |
|------|------|
| [MODELS.md](MODELS.md) | Embedding 模型选择和下载指南 |
| [SKILL.md](SKILL.md) | Meta-skill 定义（英文） |

---

## 🎨 设计理念

### 灵犀 (Spark)

> "身无彩凤双飞翼，心有灵犀一点通"

- 理解用户意图的火花
- 语义相似度匹配
- 中英双语支持

### 妙计 (Satchel)

> "锦囊妙计，随需随取"

- 装满技能的锦囊
- 审慎决策机制
- 持续学习优化

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 🙏 致谢

- [ChromaDB](https://github.com/chroma-core/chroma) - 优秀的向量数据库
- [sentence-transformers](https://github.com/UKPLab/sentence-transformers) - 强大的文本 Embedding
- 所有贡献者和使用者

---

<div align="center">

**让每一次技能调用都精准到位** ⚡

适用于 Claude Code、Cursor、Windsurf、Trae 等所有 AI IDE

🐝 Made with ❤️ by <a href="https://github.com/codestyle-mafeng">Codestyle Team</a>

</div>
