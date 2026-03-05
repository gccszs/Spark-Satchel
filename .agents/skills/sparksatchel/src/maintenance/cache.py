"""
缓存管理模块

监控数据库大小，提供清理策略
"""

import os
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from src.storage.history import HistoryTracker


class CleanupTrigger(Enum):
    """清理触发条件"""
    SIZE_LIMIT = "size"           # 大小超限
    COUNT_LIMIT = "count"         # 数量超限
    OLD_RECORDS = "old"           # 旧记录过多
    MANUAL = "manual"             # 手动触发


class CleanupStrategy:
    """清理策略"""

    @staticmethod
    def by_age(days: int = 30) -> dict:
        """按时间清理：删除 N 天前的记录

        Args:
            days: 保留最近 N 天的记录

        Returns:
            策略配置
        """
        return {
            "type": "age",
            "days": days,
            "description": f"删除 {days} 天前的记录"
        }

    @staticmethod
    def by_count(keep: int = 1000) -> dict:
        """按数量清理：保留最近 N 条

        Args:
            keep: 保留最近 N 条记录

        Returns:
            策略配置
        """
        return {
            "type": "count",
            "keep": keep,
            "description": f"保留最近 {keep} 条记录"
        }

    @staticmethod
    def by_success_rate(min_rate: float = 0.5) -> dict:
        """按成功率清理：删除低成功率记录

        Args:
            min_rate: 最低保留成功率

        Returns:
            策略配置
        """
        return {
            "type": "success_rate",
            "min_rate": min_rate,
            "description": f"删除成功率低于 {min_rate:.0%} 的记录"
        }

    @staticmethod
    def by_size(max_size_mb: int = 100) -> dict:
        """按大小清理：限制数据库大小

        Args:
            max_size_mb: 最大大小（MB）

        Returns:
            策略配置
        """
        return {
            "type": "size",
            "max_size_mb": max_size_mb,
            "description": f"限制数据库大小为 {max_size_mb}MB"
        }


@dataclass
class CleanupReport:
    """清理报告"""
    trigger: CleanupTrigger
    strategy_used: dict
    records_before: int
    records_after: int
    size_before_mb: float
    size_after_mb: float
    records_deleted: int


@dataclass
class HealthStatus:
    """缓存健康状态"""
    needs_cleanup: bool
    reason: str = ""
    suggestion: str = ""
    can_auto_cleanup: bool = True
    current_size_mb: float = 0
    record_count: int = 0


class CacheManager:
    """缓存管理器"""

    # 清理阈值
    THRESHOLDS = {
        "max_size_mb": 500,           # 最大数据库大小（MB）
        "max_records": 10000,          # 最大记录数
        "old_days": 30,                # 旧记录阈值（天）
        "old_ratio": 0.3               # 旧记录比例阈值
    }

    def __init__(
        self,
        history_tracker: HistoryTracker = None,
        data_dir: str = None
    ):
        """初始化缓存管理器

        Args:
            history_tracker: 历史记录追踪器
            data_dir: 数据目录
        """
        self.history = history_tracker or HistoryTracker()

        if data_dir is None:
            data_dir = os.path.join(
                os.path.dirname(__file__),
                "..", "..", "data"
            )

        self.data_dir = Path(data_dir)

    def check_health(self) -> HealthStatus:
        """检查缓存健康状态

        Returns:
            健康状态
        """
        # 获取当前状态
        size_bytes = self.history.get_db_size()
        size_mb = size_bytes / (1024 * 1024)
        record_count = self.history.get_record_count()

        # 检查各项阈值
        triggers = []

        if size_mb > self.THRESHOLDS["max_size_mb"]:
            triggers.append(
                f"数据库已达 {size_mb:.1f}MB"
            )

        if record_count > self.THRESHOLDS["max_records"]:
            triggers.append(
                f"已累积 {record_count:,} 条调用历史"
            )

        # TODO: 检查旧记录比例
        # old_ratio = self._calculate_old_record_ratio()
        # if old_ratio > self.THRESHOLDS["old_ratio"]:
        #     triggers.append(f"发现 {old_ratio:.0%} 的旧记录")

        if triggers:
            return HealthStatus(
                needs_cleanup=True,
                reason="；".join(triggers),
                description=self._suggest_cleanup(size_mb, record_count),
                can_auto_cleanup=self._is_auto_cleanup_safe(),
                current_size_mb=size_mb,
                record_count=record_count
            )

        return HealthStatus(
            needs_cleanup=False,
            current_size_mb=size_mb,
            record_count=record_count
        )

    def _suggest_cleanup(self, size_mb: float, record_count: int) -> str:
        """生成清理建议

        Args:
            size_mb: 当前大小
            record_count: 记录数量

        Returns:
            建议文本
        """
        if size_mb > self.THRESHOLDS["max_size_mb"]:
            return f"建议清理 30 天前的记录以释放空间"

        if record_count > self.THRESHOLDS["max_records"]:
            return f"建议保留最近 1000 条记录"

        return "建议进行缓存清理"

    def _is_auto_cleanup_safe(self) -> bool:
        """判断是否可以自动清理

        Returns:
            是否安全
        """
        # TODO: 实现更复杂的安全检查
        return True

    def cleanup(
        self,
        strategy: dict,
        dry_run: bool = False
    ) -> CleanupReport:
        """执行清理

        Args:
            strategy: 清理策略
            dry_run: 是否为演练模式（不实际删除）

        Returns:
            清理报告
        """
        # 记录清理前状态
        records_before = self.history.get_record_count()
        size_before = self.history.get_db_size()

        # 执行清理
        records_deleted = 0

        if strategy["type"] == "age":
            if not dry_run:
                records_deleted = self.history.cleanup_old_records(
                    days=strategy["days"]
                )
            else:
                records_deleted = self._estimate_age_cleanup(strategy["days"])

        elif strategy["type"] == "count":
            # TODO: 实现按数量清理
            pass

        elif strategy["type"] == "size":
            # TODO: 实现按大小清理
            pass

        # 记录清理后状态
        records_after = self.history.get_record_count()
        size_after = self.history.get_db_size()

        return CleanupReport(
            trigger=CleanupTrigger.MANUAL,
            strategy_used=strategy,
            records_before=records_before,
            records_after=records_after,
            size_before_mb=size_before / (1024 * 1024),
            size_after_mb=size_after / (1024 * 1024),
            records_deleted=records_deleted
        )

    def _estimate_age_cleanup(self, days: int) -> int:
        """估算按时间清理会删除多少记录

        Args:
            days: 天数

        Returns:
            估算的删除数量
        """
        # TODO: 实现估算逻辑
        return 0

    def auto_cleanup_if_needed(self) -> Optional[CleanupReport]:
        """如果需要则自动清理

        Returns:
            清理报告，如果不需要清理则返回 None
        """
        health = self.check_health()

        if not health.needs_cleanup:
            return None

        if not health.can_auto_cleanup:
            return None

        # 使用默认策略
        strategy = CleanupStrategy.by_age(days=30)
        return self.cleanup(strategy)

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息

        Returns:
            统计信息字典
        """
        health = self.check_health()

        return {
            "size_mb": health.current_size_mb,
            "record_count": health.record_count,
            "needs_cleanup": health.needs_cleanup,
            "reason": health.reason,
            "suggestion": health.suggestion
        }

    def clear_all(self) -> bool:
        """清空所有缓存

        Returns:
            是否成功
        """
        try:
            self.history.clear_all()
            return True
        except Exception:
            return False
