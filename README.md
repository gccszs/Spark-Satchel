<div align="center">

# 🧠 SparkSatchel 灵犀妙计

**智能技能检索与推荐系统**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Embedding](https://img.shields.io/badge/Embedding-50%2B%20Languages-orange)](#embedding-模型)

[English](./README_EN.md) | **中文**

🌈 🧠 🌈

**"身无彩凤双飞翼，心有灵犀一点通"**

灵犀妙计帮助你和你的 Agent 从万千技能中推断出你最适合当前任务的技能。

不一样的花火！⚡

*适用于 Claude Code、Cursor、Windsurf、Trae 等所有 AI IDE*

</div>

---

## 📖 目录

- [简介](#-简介)
- [与 find-skills 的关系](#️-与-find-skills-的关系)
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

## 🤝 与 find-skills 的关系

**这两个技能不是竞争关系，而是互补关系！** 它们解决的问题完全不同。
<img width="1745" height="1065" alt="image" src="https://github.com/user-attachments/assets/eff544e4-6f47-4877-b9a5-210cc295c8d3" />

### 核心区别一览表
| 维度 |  灵犀妙计 | find-skills  |
|-----------|---------------|--------------|
| **定位** | 本地智能推荐引擎 | 在线技能发现工具 |
| **搜索范围** | 只搜索已安装的本地技能 | 搜索整个 skills.sh 生态系统 |
| **工作方式** | 语义嵌入 + 向量数据库 | 关键词匹配 + 在线搜索 |
| **主要功能** | 从已有技能中选择最合适的 | 发现并安装新技能 |
| **网络依赖** | ✅ 完全离线工作 | ❌ 需要网络连接 |
| **学习能力** | ✅ 历史反馈学习 | ❌ 无学习机制 |
| **推荐理由** | 基于置信度 + 历史成功率 | 基于关键词匹配度 |

### 📊 详细对比

#### 1. SparkSatchel 灵犀妙计

```
本地技能库 (~/.claude/skills/)
    ↓
语义嵌入 (paraphrase-multilingual-MiniLM-L12-v2)
    ↓
向量相似度匹配
    ↓
置信度评分 + 历史学习
    ↓
推荐已安装的技能
```

**特点：**
- 🧠 **智能理解**：用语义嵌入理解您的意图，不只是关键词匹配
- 📚 **本地检索**：只看您电脑上已经安装的技能
- 📈 **越用越聪明**：记录您的使用反馈，优化推荐
- 🎯 **置信度机制**：高置信度自动推荐，低置信度询问用户
- 🌏 **双语支持**：中文和英文都能理解

**典型场景：**
```
您："帮我处理这个PDF"
灵犀："推荐 pdf-skill（92%成功率），因为这是 PDF 文档处理"
```

#### 2. find-skills

```
您的需求
    ↓
npx skills find [关键词]
    ↓
搜索 skills.sh 生态系统
    ↓
返回可安装的技能包
    ↓
安装新技能到本地
```

**特点：**
- 🌐 **生态搜索**：搜索整个开放的技能市场
- 📦 **安装导向**：目的是帮您找到并安装新技能
- 🔑 **关键词匹配**：通过关键词搜索技能仓库
- 🔗 **GitHub 集成**：直接从 GitHub 安装技能
- 🆕 **发现新能力**：帮您扩展 AI 的功能边界

**典型场景：**
```
您："有没有 React 性能优化的技能？"
find-skills："找到了 react-best-practices，
           运行 npx skills add xxx/react-best-practices 安装"
```

### 🤝 实际上它们是这样配合的

```
┌─────────────────────────────────────────────────────────┐
│  用户需求："我想做产品讨论"                              │
└─────────────────────────────────────────────────────────┘
                     ↓
      ┌────────────────┴────────────────┐
      ↓                                  ↓
┌─────────────────┐              ┌────────────────────┐
│  灵犀妙计       │              │  find-skills        │
│  (本地检索)     │              │  (在线搜索)        │
├─────────────────┤              ├────────────────────┤
│ ✓ 搜索本地技能  │              │ ✓ 搜索 skills.sh   │
│ ✓ 找到已安装的  │              │ ✓ 发现新技能       │
│   brainstorming │              │   discussion-skill │
│ ✓ 推荐使用      │              │ ✓ 提供安装命令     │
└─────────────────┘              └────────────────────┘
      ↓                                  ↓
  【直接使用】                      【安装后再用】
```

### 💡 实战建议

| 场景 | 应该用谁？ |
|------|----------|
| "我现在有哪些技能可以用？" | 灵犀妙计 ✅ |
| "有没有能做 XXX 的技能？" | find-skills ✅ |
| "帮我选个最合适的技能" | 灵犀妙计 ✅ |
| "我想安装新技能扩展功能" | find-skills ✅ |
| "哪个技能处理这个任务最成功？" | 灵犀妙计 ✅ |
| "社区里有 XXX 相关的技能吗？" | find-skills ✅ |

### 🎯 结论

**它们不是竞争对手，而是最佳拍档！**

正确的工作流应该是：

1. **先用灵犀妙计**看看本地有没有合适的技能
2. 如果本地没有，**再用 find-skills** 去社区搜索安装
3. 安装后，**灵犀妙计**就能智能推荐这个新技能了

---

## 🚀 快速开始

### 方式一：npx 安装（推荐）

```bash
# 使用 npx 快速安装技能
npx skills add gccszs/Spark-Satchel

# 安装完成即可使用，无需额外配置
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
