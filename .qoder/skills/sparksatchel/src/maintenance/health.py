"""
技能健康检查模块

检测技能是否缺失、损坏或版本不匹配
"""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from enum import Enum
from dataclasses import dataclass


class HealthStatus(Enum):
    """健康状态"""
    HEALTHY = "healthy"              # 技能正常
    MISSING = "missing"              # 技能不存在
    CORRUPTED = "corrupted"          # 技能损坏（如 SKILL.md 缺失）
    VERSION_MISMATCH = "outdated"    # 版本不匹配
    UNKNOWN = "unknown"              # 未知状态


@dataclass
class HealthReport:
    """健康报告"""
    skill_name: str
    status: HealthStatus
    message: str
    suggested_action: str = ""


class HealthChecker:
    """技能健康检查器"""

    def __init__(self, skills_dir: str = None):
        """初始化健康检查器

        Args:
            skills_dir: 技能目录路径
        """
        if skills_dir is None:
            skills_dir = os.path.expanduser("~/.claude/skills")

        self.skills_dir = Path(skills_dir)

    def check_skill(
        self,
        skill_name: str,
        expected_hash: str = None
    ) -> HealthReport:
        """检查单个技能的健康状态

        Args:
            skill_name: 技能名称
            expected_hash: 期望的文件哈希（用于版本检查）

        Returns:
            健康报告
        """
        skill_path = self.skills_dir / skill_name

        # 检查技能是否存在
        if not skill_path.exists():
            return HealthReport(
                skill_name=skill_name,
                status=HealthStatus.MISSING,
                message=f"技能目录不存在: {skill_path}",
                suggested_action="请重新安装该技能或检查技能目录"
            )

        # 检查关键文件
        required_files = ["SKILL.md"]
        missing_files = [
            f for f in required_files
            if not (skill_path / f).exists()
        ]

        if missing_files:
            return HealthReport(
                skill_name=skill_name,
                status=HealthStatus.CORRUPTED,
                message=f"缺少关键文件: {', '.join(missing_files)}",
                suggested_action="请重新安装该技能"
            )

        # 检查版本（如果提供了哈希）
        if expected_hash:
            current_hash = self._calculate_hash(skill_path)
            if current_hash != expected_hash:
                return HealthReport(
                    skill_name=skill_name,
                    status=HealthStatus.VERSION_MISMATCH,
                    message=f"技能版本已变更（哈希不匹配）",
                    suggested_action="建议更新技能元数据并迁移历史记录"
                )

        return HealthReport(
            skill_name=skill_name,
            status=HealthStatus.HEALTHY,
            message="技能健康",
            suggested_action=""
        )

    def check_all_skills(
        self,
        skill_list: List[str] = None,
        hash_map: Dict[str, str] = None
    ) -> List[HealthReport]:
        """检查所有技能的健康状态

        Args:
            skill_list: 技能名称列表，None 表示检查目录下所有技能
            hash_map: 技能哈希映射

        Returns:
            健康报告列表
        """
        if skill_list is None:
            skill_list = [
                d.name for d in self.skills_dir.iterdir()
                if d.is_dir() and not d.name.startswith(".")
            ]

        reports = []
        for skill_name in skill_list:
            expected_hash = hash_map.get(skill_name) if hash_map else None
            report = self.check_skill(skill_name, expected_hash)
            reports.append(report)

        return reports

    def _calculate_hash(self, skill_path: Path) -> str:
        """计算技能目录的哈希值

        Args:
            skill_path: 技能目录路径

        Returns:
            SHA256 哈希值
        """
        # 简单实现：计算 SKILL.md 的哈希
        skill_file = skill_path / "SKILL.md"
        if not skill_file.exists():
            return ""

        sha256 = hashlib.sha256()
        with open(skill_file, "rb") as f:
            sha256.update(f.read())

        return sha256.hexdigest()

    def get_unhealthy_skills(
        self,
        skill_list: List[str] = None
    ) -> List[HealthReport]:
        """获取所有不健康的技能

        Args:
            skill_list: 技能名称列表

        Returns:
            不健康技能的报告列表
        """
        all_reports = self.check_all_skills(skill_list)
        return [
            r for r in all_reports
            if r.status != HealthStatus.HEALTHY
        ]

    def fix_missing_skill(self, skill_name: str) -> bool:
        """尝试修复缺失的技能

        Args:
            skill_name: 技能名称

        Returns:
            是否修复成功
        """
        # TODO: 实现自动修复逻辑
        # 例如：从备份恢复、从 GitHub 重新下载等
        return False
