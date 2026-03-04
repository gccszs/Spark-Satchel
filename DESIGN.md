# SparkSatchel 灵犀妙计 - Meta-Skill 设计文档

**英文名**: SparkSatchel
**中文名**: 灵犀妙计
**版本**: 1.0
**日期**: 2026-03-04
**状态**: 设计完成，待实现

---

## 🎯 项目命名

```
┌─────────────────────────────────────────────────────────┐
│  灵犀妙计 (SparkSatchel)                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  灵犀 - "心有灵犀一点通"，理解用户意图                   │
│  妙计 - 锦囊妙计，每个技能都是解决问题的妙招             │
│                                                         │
│  Spark - 思维的火花点亮正确的技能                        │
│  Satchel - 装满技能的锦囊，随需随取                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 目录

1. [概述](#概述)
2. [核心功能](#核心功能)
3. [技术架构](#技术架构)
4. [决策机制](#决策机制)
5. [生命周期管理](#生命周期管理)
6. [缓存管理](#缓存管理)
7. [项目结构](#项目结构)

---

## 概述

**灵犀妙计 (SparkSatchel)** 是一个 Meta-Skill（管理技能的技能），为 Claude Code 提供智能技能检索、推荐和调用决策能力。

### 设计理念

> "三思而后行，让用户无负担"

- **智能推荐**：基于意图和历史自动推荐最合适的技能
- **审慎决策**：拿不定主意时主动询问用户
- **持续学习**：记录调用历史，优化推荐准确性
- **优雅维护**：智能检测缓存膨胀，提示清理时机

### 适用场景

```
用户: "处理这个PDF"
Agent: [内部检索] → 推荐 pdf-skill
Agent: "我建议用 pdf-skill，因为它专门处理 PDF 文档（历史成功率 92%）"

用户: "创建一个项目"
Agent: [内部检索] → 发现多个匹配
Agent: "project-start-skill 适合基于模板创建项目，是要用它吗？"
```

---

## 核心功能

### 1. 智能检索

- **语义匹配**：基于 embedding 的向量相似度搜索
- **关键词匹配**：技能描述和触发词匹配
- **分库检索**：按类别分库，提升检索效率
- **中英双语**：支持中英文技能描述

### 2. 意图推断

```
用户请求 → 预处理 → Embedding → 向量检索 → 候选技能排序
```

### 3. 置信度评估

| 置信度 | 阈值 | 行为 |
|--------|------|------|
| 高 | >70% | 自动推荐 + 说明理由 |
| 中 | 40-70% | 推荐首选 + 备选选项 |
| 低 | <40% | 展示候选 + 询问用户 |

### 4. 历史学习

- 记录每次技能调用
- 追踪成功/失败反馈
- 计算技能成功率
- 优化推荐排序

### 5. 生命周期管理

- **健康检查**：检测技能是否存在、版本是否变更
- **降级策略**：主技能失效时推荐替代技能
- **版本迁移**：技能更新时迁移历史记录

### 6. 缓存管理

- 监控数据库大小
- 检测历史记录数量
- 智能提示清理时机
- 支持自动/手动清理

---

## 技术架构

### 技术栈

```
Python 3.10+
├── chromadb>=0.5.0              # 向量数据库
├── sentence-transformers>=2.7.0 # Embedding
├── numpy>=1.24.0                # 向量运算
└── sqlite3                      # 历史记录（内置）
```

### Embedding 模型

```
paraphrase-multilingual-MiniLM-L12-v2
- 支持 50+ 语言
- 中英双语优化
- 大小: 470MB
- 速度: 快
```

### 分库策略

```
skills.db/
├── document/     # 文档处理类
│   ├── pdf
│   ├── docx
│   ├── pptx
│   └── xlsx
├── ai_tools/     # AI 工具类
│   ├── agent-call
│   ├── autogpt-agents
│   └── brainstorming
├── dev/          # 开发工具类
│   ├── skill-creator
│   ├── skill-lookup
│   └── git-worktrees
└── utility/      # 通用工具类
    ├── disk-cleaner
    ├── work-log
    └── humanizer
```

---

## 决策机制

### 决策流程

```
┌─────────────────────────────────────────────────────────┐
│  用户请求                                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  意图推断                                                 │
│  - 提取关键词                                             │
│  - 计算 embedding                                         │
│  - 向量检索                                               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  候选技能获取                                             │
│  - 语义相似度排序                                         │
│  - 历史成功率加权                                         │
│  - 技能健康检查                                           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  置信度评估                                               │
│  - 相似度分数                                             │
│  - 历史置信度                                             │
│  - 技能数量                                               │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
    [高置信度]        [中置信度]        [低置信度]
    >70%              40-70%            <40%
        ↓                 ↓                 ↓
   自动推荐          推荐+备选          询问用户
```

### 置信度计算

```python
confidence = (
    similarity_score * 0.5 +      # 语义相似度
    historical_confidence * 0.3 +  # 历史成功率
    match_count_bonus * 0.2       # 匹配数量加成
)
```

---

## 生命周期管理

### 技能状态

```
┌─────────────────────────────────────────────────────────┐
│  技能生命周期                                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [活跃] ──→ [缺失] ──→ [降级]                            │
│    ↑          │          │                               │
│    └──────────┴──────────┘                               │
│         更新/重新安装                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 健康检查

```python
class HealthStatus(Enum):
    HEALTHY = "healthy"              # 技能正常
    MISSING = "missing"              # 技能不存在
    CORRUPTED = "corrupted"          # 技能损坏
    VERSION_MISMATCH = "outdated"    # 版本不匹配

def check_skill_health(skill_path: str) -> HealthStatus:
    if not os.path.exists(skill_path):
        return HealthStatus.MISSING
    if not is_skill_valid(skill_path):
        return HealthStatus.CORRUPTED
    if has_version_changed(skill_path):
        return HealthStatus.VERSION_MISMATCH
    return HealthStatus.HEALTHY
```

### 降级策略

```python
FALLBACK_MAP = {
    "pdf-skill": ["docx-skill", "generic-document-skill"],
    "autogpt-agents": ["agent-call", "manual-creation"],
    # ...
}

def get_fallback_skill(skill_name: str) -> str:
    """获取降级技能"""
    return FALLBACK_MAP.get(skill_name, [])
```

### 版本迁移

```python
{
    "name": "pdf-skill",
    "version": "2.1.0",
    "file_hash": "sha256:abc123...",
    "migration_map": {
        "v1": "migrate_v1_to_v2",
        "v2": "current"
    }
}
```

---

## 缓存管理

### 清理触发条件

| 触发条件 | 阈值 | 提示消息 |
|----------|------|----------|
| 数据库大小 | >500MB | "🗑️ 缓存已膨胀至 500MB+，建议清理历史记录" |
| 历史记录数 | >10000 | "📝 已累积 10000+ 条调用历史，要清理吗？" |
| 旧记录比例 | >30% | "🕰️ 发现有 672 条 30 天前的旧记录" |

### 清理策略

```python
class CleanupStrategy:
    """清理策略"""

    @staticmethod
    def by_age(days: int = 30):
        """按时间清理：删除 N 天前的记录"""
        cutoff = datetime.now() - timedelta(days=days)
        return delete_records_before(cutoff)

    @staticmethod
    def by_count(keep: int = 1000):
        """按数量清理：保留最近 N 条"""
        return keep_recent_records(keep)

    @staticmethod
    def by_success_rate(min_rate: float = 0.5):
        """按成功率清理：删除低成功率记录"""
        return delete_low_success_records(min_rate)
```

### 智能提示

```python
def check_cleanup_needed():
    """检查是否需要清理"""
    size_mb = get_db_size()
    record_count = get_history_count()
    old_ratio = get_old_record_ratio()

    if size_mb > 500 or record_count > 10000 or old_ratio > 0.3:
        return {
            "needs_cleanup": True,
            "reason": format_cleanup_reason(size_mb, record_count, old_ratio),
            "suggestion": suggest_cleanup_strategy(),
            "can_auto_cleanup": is_auto_cleanup_safe()
        }
    return {"needs_cleanup": False}
```

---

## 项目结构

```
SparkSatchel/
├── SKILL.md              # Meta-skill 定义
├── README.md             # 使用说明
├── requirements.txt      # 依赖列表
├── DESIGN.md             # 本文档
│
├── src/                  # 源代码
│   ├── __init__.py
│   ├── retriever.py      # 主入口
│   │
│   ├── models/           # 模型层
│   │   ├── __init__.py
│   │   └── embedding.py  # Embedding 模型封装
│   │
│   ├── storage/          # 存储层
│   │   ├── __init__.py
│   │   ├── vector_db.py  # ChromaDB + 分库逻辑
│   │   └── history.py    # SQLite 历史记录
│   │
│   ├── analysis/         # 分析层
│   │   ├── __init__.py
│   │   ├── intent.py     # 意图推断
│   │   └── confidence.py # 置信度评估
│   │
│   ├── decision.py       # 决策引擎
│   │
│   └── maintenance/      # 维护模块
│       ├── __init__.py
│       ├── health.py     # 健康检查
│       ├── lifecycle.py  # 生命周期管理
│       └── cache.py      # 缓存清理
│
└── data/                 # 数据目录
    ├── collections/      # 分库存储
    │   ├── document/
    │   ├── ai_tools/
    │   ├── dev/
    │   └── utility/
    ├── history.db        # 调用历史
    └── cache/            # 缓存目录
        └── models/       # 模型缓存
```

---

## 数据模型

### 技能元数据

```json
{
  "name": "pdf-skill",
  "path": "/path/to/skill",
  "description": "PDF文档处理",
  "tags": ["文档", "PDF", "提取"],
  "trigger_keywords": ["PDF", "pdf", "提取PDF"],
  "category": "document",
  "version": "2.1.0",
  "file_hash": "sha256:abc123...",
  "signature": "v2",
  "deprecated": false,
  "installed_at": "2026-03-01T00:00:00Z",
  "last_updated": "2026-03-04T00:00:00Z"
}
```

### 调用历史

```json
{
  "id": "uuid",
  "timestamp": "2026-03-04T10:00:00Z",
  "user_request": "处理这个PDF",
  "intent": "pdf_processing",
  "matched_skills": ["pdf-skill", "docx-skill"],
  "recommended_skill": "pdf-skill",
  "confidence": 0.85,
  "user_accepted": true,
  "execution_success": true,
  "user_feedback": "good"
}
```

---

## API 设计

### 主接口

```python
class SparkSatchel:
    """技能检索器主接口"""

    def retrieve(self, user_request: str) -> RetrievalResult:
        """检索并推荐技能

        Args:
            user_request: 用户请求文本

        Returns:
            RetrievalResult: 检索结果
        """
        pass

    def record_call(self, call: SkillCall):
        """记录技能调用"""
        pass

    def feedback(self, skill_name: str, success: bool, feedback: str = ""):
        """记录用户反馈"""
        pass

    def check_health(self) -> HealthReport:
        """检查系统健康状态"""
        pass

    def cleanup(self, strategy: CleanupStrategy):
        """执行缓存清理"""
        pass
```

### 检索结果

```python
@dataclass
class RetrievalResult:
    """检索结果"""

    confidence: float              # 置信度 0-1
    recommended_skill: str         # 推荐的技能

    # 中置信度时提供备选
    alternative_skills: List[str] = field(default_factory=list)

    # 低置信度时提供候选列表
    candidate_skills: List[Dict[str, Any]] = field(default_factory=list)

    # 推荐理由
    reasoning: str = ""

    # 是否需要用户确认
    requires_confirmation: bool = False
```

---

## 使用示例

### 基本使用

```python
from src.retriever import SparkSatchel

sparksatchel = SparkSatchel()

# 高置信度 - 自动推荐
result = sparksatchel.retrieve("处理这个PDF")
print(result.reasoning)
# "建议用 pdf-skill，因为它专门处理 PDF 文档（历史成功率 92%）"

# 中置信度 - 推荐 + 备选
result = sparksatchel.retrieve("创建文档")
print(result.reasoning)
# "建议用 docx-skill，pdf-skill 也可以，要我详细对比吗？"

# 低置信度 - 询问用户
result = sparksatchel.retrieve("处理数据")
print(result.candidate_skills)
# ["xlsx-skill", "pandas-skill", "csv-skill"]
```

### 反馈学习

```python
# 记录调用成功
sparksatchel.feedback("pdf-skill", success=True, feedback="很好用")

# 记录调用失败
sparksatchel.feedback("pdf-skill", success=False, feedback="格式不支持")
```

### 缓存清理

```python
from src.maintenance.cache import CleanupStrategy

# 检查是否需要清理
health = sparksatchel.check_health()
if health.needs_cleanup:
    print(health.reasoning)

# 执行清理
sparksatchel.cleanup(CleanupStrategy.by_age(days=30))
```

---

## 实现优先级

### P0 - 核心功能
- [ ] 基础向量检索（ChromaDB + Embedding）
- [ ] 简单意图推断
- [ ] 置信度评估
- [ ] 基础决策逻辑

### P1 - 智能化
- [ ] 历史记录追踪
- [ ] 成功率计算
- [ ] 推荐理由生成
- [ ] 候选技能排序优化

### P2 - 生命周期
- [ ] 技能健康检查
- [ ] 降级策略
- [ ] 版本迁移

### P3 - 维护
- [ ] 缓存监控
- [ ] 清理提示
- [ ] 自动清理策略

---

## 性能指标

| 指标 | 目标 | 说明 |
|------|------|------|
| 检索延迟 | <500ms | 10万技能库 |
| 内存占用 | <500MB | 包含模型和向量库 |
| 启动时间 | <3s | 首次加载模型 |
| 准确率 | >85% | 推荐技能符合用户意图 |

---

## 扩展性

### 从 ChromaDB 迁移到 Qdrant

```python
# 存储层抽象，便于迁移
class VectorStore(ABC):
    @abstractmethod
    def add(self, collection: str, documents: List[Document]):
        pass

    @abstractmethod
    def search(self, collection: str, query: str, top_k: int):
        pass

# ChromaDB 实现
class ChromaDBStore(VectorStore):
    # ...

# Qdrant 实现（未来）
class QdrantStore(VectorStore):
    # ...
```

### 分库扩展

```python
# 当技能数超过 10 万时，增加新的分库
NEW_COLLECTIONS = {
    "media": ["image", "video", "audio"],
    "database": ["mysql", "postgres", "mongodb"],
    # ...
}
```

---

## 安全与隐私

- **本地优先**：所有数据存储在本地，不上传云端
- **无追踪**：不收集用户数据
- **透明性**：用户可查看所有历史记录
- **可控性**：用户可随时删除历史记录

---

## 许可证

MIT License

---

**文档版本**: 1.0
**最后更新**: 2026-03-04
