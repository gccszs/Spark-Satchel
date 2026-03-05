"""
置信度评估模块

评估技能推荐的置信度，综合考虑多种因素
"""

from typing import List, Optional
from dataclasses import dataclass
from src.storage.vector_db import SearchResult
from src.storage.history import SkillStats


@dataclass
class ConfidenceBreakdown:
    """置信度分解"""
    total: float                # 总置信度
    similarity: float           # 语义相似度
    historical: float           # 历史成功率
    relevance: float            # 相关性分数
    freshness: float            # 最近使用加成


class ConfidenceEvaluator:
    """置信度评估器"""

    # 权重配置
    WEIGHTS = {
        "similarity": 0.5,      # 语义相似度权重
        "historical": 0.3,      # 历史成功率权重
        "relevance": 0.15,      # 相关性权重
        "freshness": 0.05       # 最近使用加成
    }

    # 置信度阈值
    THRESHOLDS = {
        "high": 0.70,           # 高置信度阈值
        "medium": 0.40,         # 中置信度阈值
        "low": 0.0              # 低置信度阈值
    }

    def __init__(self, weights: dict = None):
        """初始化评估器

        Args:
            weights: 自定义权重
        """
        if weights:
            self.WEIGHTS.update(weights)

    def evaluate(
        self,
        search_result: SearchResult,
        stats: Optional[SkillStats] = None,
        num_candidates: int = 1
    ) -> ConfidenceBreakdown:
        """评估单个结果的置信度

        Args:
            search_result: 搜索结果
            stats: 技能统计信息
            num_candidates: 候选技能数量

        Returns:
            置信度分解
        """
        # 计算各维度分数
        similarity = self._similarity_score(search_result.similarity)
        historical = self._historical_score(stats)
        relevance = self._relevance_score(search_result, num_candidates)
        freshness = self._freshness_score(stats)

        # 加权求和
        total = (
            similarity * self.WEIGHTS["similarity"] +
            historical * self.WEIGHTS["historical"] +
            relevance * self.WEIGHTS["relevance"] +
            freshness * self.WEIGHTS["freshness"]
        )

        return ConfidenceBreakdown(
            total=min(total, 1.0),
            similarity=similarity,
            historical=historical,
            relevance=relevance,
            freshness=freshness
        )

    def evaluate_batch(
        self,
        search_results: List[SearchResult],
        all_stats: dict
    ) -> List[ConfidenceBreakdown]:
        """批量评估

        Args:
            search_results: 搜索结果列表
            all_stats: 所有技能的统计信息映射

        Returns:
            置信度分解列表
        """
        return [
            self.evaluate(
                result,
                all_stats.get(result.skill_name),
                len(search_results)
            )
            for result in search_results
        ]

    def _similarity_score(self, similarity: float) -> float:
        """计算相似度分数

        Args:
            similarity: 原始相似度

        Returns:
            归一化后的分数 [0, 1]
        """
        # 相似度已经归一化，但可以应用非线性变换
        # 使得高相似度更突出
        return similarity ** 0.8

    def _historical_score(self, stats: Optional[SkillStats]) -> float:
        """计算历史表现分数

        Args:
            stats: 技能统计

        Returns:
            历史分数 [0, 1]
        """
        if stats is None or stats.total_calls == 0:
            # 没有历史记录，给予中性分数
            return 0.5

        # 主要考虑成功率
        success_rate = stats.success_rate

        # 调用次数也影响可信度
        call_confidence = min(stats.total_calls / 50, 1.0)  # 50次调用达到最高可信度

        # 综合评分
        return success_rate * 0.8 + call_confidence * 0.2

    def _relevance_score(self, result: SearchResult, num_candidates: int) -> float:
        """计算相关性分数

        Args:
            result: 搜索结果
            num_candidates: 候选数量

        Returns:
            相关性分数 [0, 1]
        """
        score = 1.0

        # 关键词匹配加成
        # TODO: 实现更精确的关键词匹配

        # 候选数量影响（候选越少，说明越明确）
        if num_candidates == 1:
            score *= 1.2
        elif num_candidates <= 3:
            score *= 1.1
        elif num_candidates > 10:
            score *= 0.9

        return min(score, 1.0)

    def _freshness_score(self, stats: Optional[SkillStats]) -> float:
        """计算新鲜度分数（最近使用加成）

        Args:
            stats: 技能统计

        Returns:
            新鲜度分数 [0, 1]
        """
        if stats is None or not stats.last_called:
            return 0.5

        # TODO: 实现基于时间的衰减
        # 最近使用的技能有轻微加成
        return 0.5

    def get_confidence_level(self, confidence: float) -> str:
        """获取置信度等级

        Args:
            confidence: 置信度分数

        Returns:
            等级: "high", "medium", "low"
        """
        if confidence >= self.THRESHOLDS["high"]:
            return "high"
        elif confidence >= self.THRESHOLDS["medium"]:
            return "medium"
        else:
            return "low"

    def should_ask_user(self, confidence: float) -> bool:
        """判断是否需要询问用户

        Args:
            confidence: 置信度分数

        Returns:
            是否需要询问
        """
        return confidence < self.THRESHOLDS["high"]
