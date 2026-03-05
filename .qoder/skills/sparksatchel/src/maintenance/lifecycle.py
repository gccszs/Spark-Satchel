"""
生命周期管理模块

处理技能的版本迁移、降级策略等生命周期问题
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from src.maintenance.health import HealthStatus, HealthChecker


class MigrationAction(Enum):
    """迁移动作"""
    NONE = "none"                  # 无需操作
    UPDATE_METADATA = "update"     # 更新元数据
    MIGRATE_HISTORY = "migrate"    # 迁移历史记录
    REMOVE_FROM_INDEX = "remove"   # 从索引移除


@dataclass
class MigrationPlan:
    """迁移计划"""
    skill_name: str
    action: MigrationAction
    reason: str
    steps: List[str]


class LifecycleManager:
    """生命周期管理器"""

    # 降级映射：主技能不可用时使用的备选技能
    FALLBACK_MAP = {
        "pdf-skill": ["docx-skill", "generic-document-skill"],
        "docx-skill": ["pdf-skill", "generic-document-skill"],
        "autogpt-agents": ["agent-call", "manual-creation"],
        "brainstorming": ["manual-thinking"],
        # 用户可以继续添加...
    }

    # 版本迁移映射
    VERSION_MIGRATIONS = {
        "pdf-skill": {
            "v1": "migrate_pdf_v1_to_v2",
            "v2": "current"
        }
        # 用户可以继续添加...
    }

    def __init__(self, health_checker: HealthChecker = None):
        """初始化生命周期管理器

        Args:
            health_checker: 健康检查器
        """
        self.health_checker = health_checker or HealthChecker()

    def plan_migration(
        self,
        skill_name: str,
        health_status: HealthStatus
    ) -> MigrationPlan:
        """规划迁移方案

        Args:
            skill_name: 技能名称
            health_status: 健康状态

        Returns:
            迁移计划
        """
        if health_status == HealthStatus.HEALTHY:
            return MigrationPlan(
                skill_name=skill_name,
                action=MigrationAction.NONE,
                reason="技能健康，无需迁移",
                steps=[]
            )

        elif health_status == HealthStatus.MISSING:
            return MigrationPlan(
                skill_name=skill_name,
                action=MigrationAction.REMOVE_FROM_INDEX,
                reason="技能已移除，从索引中删除",
                steps=[
                    f"1. 标记 {skill_name} 为已移除",
                    "2. 保留历史记录以供参考",
                    "3. 推荐备选技能"
                ]
            )

        elif health_status == HealthStatus.VERSION_MISMATCH:
            return MigrationPlan(
                skill_name=skill_name,
                action=MigrationAction.MIGRATE_HISTORY,
                reason="技能版本已更新",
                steps=[
                    "1. 计算新的文件哈希",
                    "2. 更新技能元数据",
                    "3. 迁移历史记录到新版本",
                    "4. 验证迁移结果"
                ]
            )

        elif health_status == HealthStatus.CORRUPTED:
            return MigrationPlan(
                skill_name=skill_name,
                action=MigrationAction.REMOVE_FROM_INDEX,
                reason="技能损坏",
                steps=[
                    "1. 从索引中移除",
                    "2. 建议用户重新安装"
                ]
            )

        return MigrationPlan(
            skill_name=skill_name,
            action=MigrationAction.NONE,
            reason="未知状态",
            steps=[]
        )

    def get_fallback_skills(self, skill_name: str) -> List[str]:
        """获取备选技能列表

        Args:
            skill_name: 主技能名称

        Returns:
            备选技能名称列表
        """
        return self.FALLBACK_MAP.get(skill_name, [])

    def add_fallback(self, primary: str, fallback: List[str]):
        """添加降级映射

        Args:
            primary: 主技能名称
            fallback: 备选技能列表
        """
        self.FALLBACK_MAP[primary] = fallback

    def check_migrations_needed(
        self,
        skill_list: List[str],
        hash_map: Dict[str, str]
    ) -> List[MigrationPlan]:
        """检查所有需要迁移的技能

        Args:
            skill_list: 技能列表
            hash_map: 技能哈希映射

        Returns:
            迁移计划列表
        """
        plans = []

        for skill_name in skill_list:
            expected_hash = hash_map.get(skill_name)
            report = self.health_checker.check_skill(skill_name, expected_hash)

            if report.status != HealthStatus.HEALTHY:
                plan = self.plan_migration(skill_name, report.status)
                plans.append(plan)

        return plans

    def migrate_skill_version(
        self,
        skill_name: str,
        old_version: str,
        new_version: str
    ) -> bool:
        """迁移技能版本

        Args:
            skill_name: 技能名称
            old_version: 旧版本
            new_version: 新版本

        Returns:
            是否迁移成功
        """
        # TODO: 实现实际的版本迁移逻辑
        # 这里需要更新数据库中的版本信息和哈希

        return True

    def deprecate_skill(
        self,
        skill_name: str,
        replacement: str = None
    ) -> bool:
        """弃用技能

        Args:
            skill_name: 要弃用的技能
            replacement: 替代技能

        Returns:
            是否成功
        """
        # TODO: 实现弃用逻辑
        # 1. 标记技能为已弃用
        # 2. 如果有替代技能，建立映射
        # 3. 更新推荐逻辑

        if replacement:
            self.add_fallback(skill_name, [replacement])

        return True
