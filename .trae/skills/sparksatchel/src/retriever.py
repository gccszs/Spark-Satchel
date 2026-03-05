"""
SparkSatchel 灵犀妙计 - 主入口

智能技能检索与推荐系统
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field

from src.models.embedding import EmbeddingModel
from src.storage.vector_db import VectorStore, SkillMetadata, SearchResult
from src.storage.history import HistoryTracker, SkillCall, SkillStats
from src.analysis.intent import IntentAnalyzer
from src.analysis.confidence import ConfidenceEvaluator
from src.decision import DecisionEngine, DecisionResult
from src.maintenance.health import HealthChecker, HealthStatus
from src.maintenance.lifecycle import LifecycleManager
from src.maintenance.cache import CacheManager, CleanupStrategy


@dataclass
class RetrievalResult:
    """检索结果"""
    confidence: float                    # 置信度 0-1
    recommended_skill: str               # 推荐的技能
    reasoning: str                       # 推荐理由

    # 中置信度时提供备选
    alternative_skills: List[str] = field(default_factory=list)

    # 低置信度时提供候选列表
    candidate_skills: List[Dict[str, Any]] = field(default_factory=list)

    # 是否需要用户确认
    requires_confirmation: bool = False

    # 内部数据（调试用）
    intent: str = ""
    matched_skills: List[str] = field(default_factory=list)


class SparkSatchel:
    """灵犀妙计 - 智能技能检索器"""

    def __init__(
        self,
        skills_dir: str = None,
        data_dir: str = None,
        auto_load: bool = True
    ):
        """初始化 SparkSatchel

        Args:
            skills_dir: 技能目录
            data_dir: 数据目录
            auto_load: 是否自动加载现有技能
        """
        # 目录设置
        if skills_dir is None:
            skills_dir = os.path.expanduser("~/.claude/skills")
        self.skills_dir = Path(skills_dir)

        if data_dir is None:
            data_dir = os.path.join(
                os.path.dirname(__file__),
                "..", "data"
            )
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 初始化组件
        self.embedding_model = EmbeddingModel.get_default()
        self.vector_store = VectorStore(
            persist_directory=str(self.data_dir / "collections"),
            embedding_model=self.embedding_model
        )
        self.history = HistoryTracker(
            db_path=str(self.data_dir / "history.db")
        )
        self.intent_analyzer = IntentAnalyzer()
        self.confidence_evaluator = ConfidenceEvaluator()
        self.decision_engine = DecisionEngine(self.confidence_evaluator)
        self.health_checker = HealthChecker(str(self.skills_dir))
        self.lifecycle_manager = LifecycleManager(self.health_checker)
        self.cache_manager = CacheManager(self.history, str(self.data_dir))

        # 加载技能
        if auto_load:
            self._load_existing_skills()

    def _load_existing_skills(self):
        """加载现有技能到向量库"""
        # TODO: 扫描技能目录并加载
        pass

    def retrieve(self, user_request: str) -> RetrievalResult:
        """检索并推荐技能

        Args:
            user_request: 用户请求文本

        Returns:
            检索结果
        """
        # 1. 意图分析
        intent = self.intent_analyzer.analyze(user_request)

        # 2. 向量检索
        search_results = self.vector_store.search(
            query=user_request,
            top_k=10,
            min_similarity=0.3
        )

        # 3. 获取历史统计
        skill_names = [r.skill_name for r in search_results]
        stats_map = {}
        for name in skill_names:
            stats = self.history.get_skill_stats(name)
            if stats:
                stats_map[name] = stats

        # 4. 决策
        decision = self.decision_engine.decide(search_results, stats_map)

        # 5. 记录这次检索
        self._record_retrieval(user_request, intent, decision)

        # 6. 构建返回结果
        return RetrievalResult(
            confidence=decision.confidence,
            recommended_skill=decision.recommended_skill,
            reasoning=decision.reasoning,
            alternative_skills=decision.alternative_skills,
            candidate_skills=decision.candidate_skills,
            requires_confirmation=decision.requires_confirmation,
            intent=intent.primary,
            matched_skills=[r.skill_name for r in search_results]
        )

    def _record_retrieval(
        self,
        user_request: str,
        intent,
        decision: DecisionResult
    ):
        """记录检索到历史

        Args:
            user_request: 用户请求
            intent: 意图对象
            decision: 决策结果
        """
        call = SkillCall(
            id=None,
            timestamp=datetime.now().isoformat(),
            user_request=user_request,
            intent=intent.primary,
            matched_skills=decision.alternative_skills + [decision.recommended_skill],
            recommended_skill=decision.recommended_skill,
            confidence=decision.confidence,
            user_accepted=False,  # 待用户确认后更新
            execution_success=None,
            user_feedback=""
        )

        # 保存到待确认队列
        # TODO: 实现待确认队列
        self._pending_call = call

    def feedback(
        self,
        skill_name: str,
        success: bool,
        feedback: str = ""
    ):
        """记录用户反馈

        Args:
            skill_name: 技能名称
            success: 是否成功
            feedback: 用户反馈
        """
        if not hasattr(self, '_pending_call'):
            return

        # 更新待确认的调用记录
        self._pending_call.user_accepted = True
        self._pending_call.execution_success = success
        self._pending_call.user_feedback = feedback

        # 记录到历史
        self.history.record_call(self._pending_call)

        # 清除待确认记录
        delattr(self, '_pending_call')

    def add_skill(self, metadata: SkillMetadata):
        """添加技能到向量库

        Args:
            metadata: 技能元数据
        """
        self.vector_store.add_skill(metadata)

    def remove_skill(self, skill_name: str, category: str):
        """从向量库移除技能

        Args:
            skill_name: 技能名称
            category: 技能分类
        """
        self.vector_store.remove_skill(skill_name, category)

    def check_health(self) -> Dict[str, Any]:
        """检查系统健康状态

        Returns:
            健康状态报告
        """
        # 检查缓存健康
        cache_health = self.cache_manager.check_health()

        # 检查技能健康
        all_stats = self.history.get_all_stats()
        skill_names = list({s.skill_name for s in all_stats})
        unhealthy = self.health_checker.get_unhealthy_skills(skill_names)

        return {
            "cache": {
                "needs_cleanup": cache_health.needs_cleanup,
                "size_mb": cache_health.current_size_mb,
                "record_count": cache_health.record_count,
                "reason": cache_health.reason
            },
            "skills": {
                "unhealthy_count": len(unhealthy),
                "unhealthy_list": [
                    {"skill": r.skill_name, "status": r.status.value}
                    for r in unhealthy[:10]  # 最多显示10个
                ]
            },
            "suggestion": self._generate_health_suggestion(cache_health, unhealthy)
        }

    def _generate_health_suggestion(
        self,
        cache_health,
        unhealthy_skills
    ) -> str:
        """生成健康建议

        Args:
            cache_health: 缓存健康状态
            unhealthy_skills: 不健康技能列表

        Returns:
            建议文本
        """
        suggestions = []

        if cache_health.needs_cleanup:
            suggestions.append(f"🗑️ {cache_health.suggestion}")

        if unhealthy_skills:
            suggestions.append(
                f"⚠️ 发现 {len(unhealthy_skills)} 个技能状态异常"
            )

        return "；".join(suggestions) if suggestions else "系统健康"

    def cleanup(self, strategy: dict = None):
        """执行缓存清理

        Args:
            strategy: 清理策略，None 则使用默认策略
        """
        if strategy is None:
            strategy = CleanupStrategy.by_age(days=30)

        report = self.cache_manager.cleanup(strategy)

        return {
            "records_deleted": report.records_deleted,
            "size_before_mb": report.size_before_mb,
            "size_after_mb": report.size_after_mb,
            "freed_mb": report.size_before_mb - report.size_after_mb
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取系统统计信息

        Returns:
            统计信息
        """
        cache_stats = self.cache_manager.get_cache_stats()
        skill_counts = self.vector_store.get_skill_count()

        return {
            "cache": cache_stats,
            "skills": {
                "total": sum(skill_counts.values()),
                "by_category": skill_counts
            }
        }

    def index_skills(self, force: bool = False):
        """扫描并索引技能目录

        Args:
            force: 是否强制重新索引
        """
        indexed_count = 0

        for skill_path in self.skills_dir.iterdir():
            if not skill_path.is_dir() or skill_path.name.startswith("."):
                continue

            # 读取 SKILL.md
            skill_md = skill_path / "SKILL.md"
            if not skill_md.exists():
                continue

            # 解析技能元数据
            metadata = self._parse_skill_md(skill_path.name, skill_md)

            if metadata:
                self.add_skill(metadata)
                indexed_count += 1

        return indexed_count

    def _parse_skill_md(self, skill_name: str, skill_md_path: Path) -> Optional[SkillMetadata]:
        """解析 SKILL.md 文件

        Args:
            skill_name: 技能名称
            skill_md_path: SKILL.md 文件路径

        Returns:
            技能元数据
        """
        try:
            content = skill_md_path.read_text(encoding="utf-8")

            # 解析 YAML frontmatter
            # TODO: 实现 YAML 解析

            # 简单实现：提取描述
            description = ""
            for line in content.split("\n"):
                if "description:" in line.lower():
                    description = line.split(":", 1)[1].strip()
                    break

            return SkillMetadata(
                name=skill_name,
                path=str(skill_md_path.parent),
                description=description,
                tags=[],
                trigger_keywords=[],
                category="utility"  # 默认分类
            )

        except Exception:
            return None


# 单例模式
_instance = None


def get_instance() -> SparkSatchel:
    """获取 SparkSatchel 单例

    Returns:
        SparkSatchel 实例
    """
    global _instance
    if _instance is None:
        _instance = SparkSatchel()
    return _instance
