"""
决策引擎

根据置信度和候选技能，做出推荐决策
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

from src.storage.vector_db import SearchResult, SkillMetadata
from src.storage.history import SkillStats
from src.analysis.confidence import ConfidenceEvaluator, ConfidenceBreakdown


class DecisionLevel(Enum):
    """决策等级"""
    AUTO_RECOMMEND = "auto"      # 自动推荐
    WITH_ALTERNATIVES = "alt"    # 带备选的推荐
    ASK_USER = "ask"             # 询问用户


@dataclass
class DecisionResult:
    """决策结果"""
    level: DecisionLevel         # 决策等级
    recommended_skill: str       # 推荐技能
    confidence: float            # 置信度
    breakdown: ConfidenceBreakdown  # 置信度分解

    # 中低置信度时提供
    alternative_skills: List[str] = field(default_factory=list)
    candidate_skills: List[Dict[str, Any]] = field(default_factory=list)

    # 推荐理由
    reasoning: str = ""

    # 是否需要用户确认
    requires_confirmation: bool = False


class DecisionEngine:
    """决策引擎"""

    def __init__(
        self,
        confidence_evaluator: ConfidenceEvaluator = None
    ):
        """初始化决策引擎

        Args:
            confidence_evaluator: 置信度评估器
        """
        self.evaluator = confidence_evaluator or ConfidenceEvaluator()

    def decide(
        self,
        search_results: List[SearchResult],
        stats_map: Dict[str, SkillStats]
    ) -> DecisionResult:
        """做出决策

        Args:
            search_results: 搜索结果列表
            stats_map: 技能统计映射

        Returns:
            决策结果
        """
        if not search_results:
            return self._no_match_result()

        # 评估所有结果
        evaluations = []
        for result in search_results:
            stats = stats_map.get(result.skill_name)
            breakdown = self.evaluator.evaluate(result, stats, len(search_results))
            evaluations.append((result, breakdown))

        # 按置信度排序
        evaluations.sort(key=lambda x: x[1].total, reverse=True)

        # 获取最佳结果
        best_result, best_breakdown = evaluations[0]

        # 根据置信度决定
        level = self.evaluator.get_confidence_level(best_breakdown.total)

        if level == "high":
            return self._auto_recommend(best_result, best_breakdown)
        elif level == "medium":
            alternatives = [e[0].skill_name for e in evaluations[1:3]]
            return self._recommend_with_alternatives(
                best_result, best_breakdown, alternatives
            )
        else:
            candidates = [
                {
                    "skill_name": r.skill_name,
                    "similarity": r.similarity,
                    "description": r.metadata.description
                }
                for r, _ in evaluations[:5]
            ]
            return self._ask_user(best_result, best_breakdown, candidates)

    def _auto_recommend(
        self,
        result: SearchResult,
        breakdown: ConfidenceBreakdown
    ) -> DecisionResult:
        """自动推荐

        Args:
            result: 最佳搜索结果
            breakdown: 置信度分解

        Returns:
            决策结果
        """
        reasoning = self._generate_reasoning(result, breakdown)

        return DecisionResult(
            level=DecisionLevel.AUTO_RECOMMEND,
            recommended_skill=result.skill_name,
            confidence=breakdown.total,
            breakdown=breakdown,
            reasoning=reasoning,
            requires_confirmation=False
        )

    def _recommend_with_alternatives(
        self,
        result: SearchResult,
        breakdown: ConfidenceBreakdown,
        alternatives: List[str]
    ) -> DecisionResult:
        """推荐带备选

        Args:
            result: 最佳搜索结果
            breakdown: 置信度分解
            alternatives: 备选技能列表

        Returns:
            决策结果
        """
        reasoning = self._generate_reasoning(result, breakdown, alternatives)

        return DecisionResult(
            level=DecisionLevel.WITH_ALTERNATIVES,
            recommended_skill=result.skill_name,
            confidence=breakdown.total,
            breakdown=breakdown,
            alternative_skills=alternatives,
            reasoning=reasoning,
            requires_confirmation=False
        )

    def _ask_user(
        self,
        result: SearchResult,
        breakdown: ConfidenceBreakdown,
        candidates: List[Dict[str, Any]]
    ) -> DecisionResult:
        """询问用户

        Args:
            result: 最佳搜索结果
            breakdown: 置信度分解
            candidates: 候选技能列表

        Returns:
            决策结果
        """
        reasoning = (
            f"找到 {len(candidates)} 个可能符合的技能，"
            f"需要你帮忙选择最合适的一个。"
        )

        return DecisionResult(
            level=DecisionLevel.ASK_USER,
            recommended_skill=result.skill_name,  # 仍然给出推荐
            confidence=breakdown.total,
            breakdown=breakdown,
            candidate_skills=candidates,
            reasoning=reasoning,
            requires_confirmation=True
        )

    def _no_match_result(self) -> DecisionResult:
        """无匹配结果

        Returns:
            决策结果
        """
        return DecisionResult(
            level=DecisionLevel.ASK_USER,
            recommended_skill="",
            confidence=0.0,
            breakdown=ConfidenceBreakdown(0, 0, 0, 0, 0),
            reasoning="未找到匹配的技能",
            requires_confirmation=True
        )

    def _generate_reasoning(
        self,
        result: SearchResult,
        breakdown: ConfidenceBreakdown,
        alternatives: List[str] = None
    ) -> str:
        """生成推荐理由

        Args:
            result: 搜索结果
            breakdown: 置信度分解
            alternatives: 备选技能

        Returns:
            推荐理由文本
        """
        parts = []

        # 主要理由
        parts.append(f"建议用 **{result.skill_name}**")

        # 描述
        if result.metadata.description:
            parts.append(f"- {result.metadata.description}")

        # 相似度
        if breakdown.similarity > 0.7:
            parts.append(f"- 与你的请求高度匹配（{breakdown.similarity:.0%}）")

        # 历史表现
        if breakdown.historical > 0.6:
            parts.append(f"- 历史使用效果良好（{breakdown.historical:.0%}）")

        # 备选
        if alternatives:
            alt_list = "、".join(alternatives[:3])
            parts.append(f"- 备选：{alt_list}")

        return "\n".join(parts)
