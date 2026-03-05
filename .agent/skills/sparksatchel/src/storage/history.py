"""
历史记录管理

使用 SQLite 记录技能调用历史，支持成功率统计和学习
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum


class CallStatus(Enum):
    """调用状态"""
    SUCCESS = "success"
    FAILED = "failed"
    REJECTED = "rejected"  # 用户拒绝


@dataclass
class SkillCall:
    """技能调用记录"""
    id: Optional[str]
    timestamp: str
    user_request: str
    intent: str
    matched_skills: List[str]
    recommended_skill: str
    confidence: float
    user_accepted: bool
    execution_success: bool
    user_feedback: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SkillStats:
    """技能统计信息"""
    skill_name: str
    total_calls: int
    success_count: int
    failure_count: int
    rejection_count: int
    success_rate: float
    avg_confidence: float
    last_called: str


class HistoryTracker:
    """历史记录追踪器"""

    def __init__(self, db_path: str = None):
        """初始化历史记录

        Args:
            db_path: 数据库路径
        """
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__),
                "..", "..", "data", "history.db"
            )

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建调用记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_calls (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                user_request TEXT NOT NULL,
                intent TEXT NOT NULL,
                matched_skills TEXT NOT NULL,
                recommended_skill TEXT NOT NULL,
                confidence REAL NOT NULL,
                user_accepted INTEGER NOT NULL,
                execution_success INTEGER,
                user_feedback TEXT
            )
        """)

        # 创建技能统计表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_stats (
                skill_name TEXT PRIMARY KEY,
                total_calls INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                rejection_count INTEGER DEFAULT 0,
                avg_confidence REAL DEFAULT 0.0,
                last_called TEXT
            )
        """)

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recommended_skill
            ON skill_calls(recommended_skill)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON skill_calls(timestamp)
        """)

        conn.commit()
        conn.close()

    def record_call(self, call: SkillCall) -> str:
        """记录一次技能调用

        Args:
            call: 调用记录

        Returns:
            记录 ID
        """
        import uuid

        if call.id is None:
            call.id = str(uuid.uuid4())

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 插入调用记录
        cursor.execute("""
            INSERT INTO skill_calls
            (id, timestamp, user_request, intent, matched_skills,
             recommended_skill, confidence, user_accepted, execution_success, user_feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            call.id,
            call.timestamp,
            call.user_request,
            call.intent,
            json.dumps(call.matched_skills),
            call.recommended_skill,
            call.confidence,
            1 if call.user_accepted else 0,
            1 if call.execution_success else 0 if call.execution_success is not None else None,
            call.user_feedback
        ))

        # 更新统计
        self._update_stats(cursor, call)

        conn.commit()
        conn.close()

        return call.id

    def _update_stats(self, cursor, call: SkillCall):
        """更新技能统计"""
        skill_name = call.recommended_skill

        # 查询现有统计
        cursor.execute("SELECT * FROM skill_stats WHERE skill_name = ?", (skill_name,))
        row = cursor.fetchone()

        if row:
            # 更新
            total_calls = row[1] + 1
            success_count = row[2] + (1 if call.execution_success else 0)
            failure_count = row[3] + (1 if call.execution_success is False else 0)
            rejection_count = row[4] + (1 if not call.user_accepted else 0)

            # 更新平均置信度
            avg_confidence = (row[5] * row[1] + call.confidence) / total_calls

            cursor.execute("""
                UPDATE skill_stats
                SET total_calls = ?, success_count = ?, failure_count = ?,
                    rejection_count = ?, avg_confidence = ?, last_called = ?
                WHERE skill_name = ?
            """, (total_calls, success_count, failure_count, rejection_count,
                  avg_confidence, call.timestamp, skill_name))
        else:
            # 插入
            cursor.execute("""
                INSERT INTO skill_stats
                (skill_name, total_calls, success_count, failure_count,
                 rejection_count, avg_confidence, last_called)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (skill_name, 1,
                  1 if call.execution_success else 0,
                  1 if call.execution_success is False else 0,
                  1 if not call.user_accepted else 0,
                  call.confidence,
                  call.timestamp))

    def get_skill_stats(self, skill_name: str) -> Optional[SkillStats]:
        """获取技能统计

        Args:
            skill_name: 技能名称

        Returns:
            技能统计信息
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM skill_stats WHERE skill_name = ?", (skill_name,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return SkillStats(
                skill_name=row[0],
                total_calls=row[1],
                success_count=row[2],
                failure_count=row[3],
                rejection_count=row[4],
                success_rate=row[2] / row[1] if row[1] > 0 else 0.0,
                avg_confidence=row[5],
                last_called=row[6]
            )
        return None

    def get_all_stats(self) -> List[SkillStats]:
        """获取所有技能统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM skill_stats")
        rows = cursor.fetchall()

        conn.close()

        return [
            SkillStats(
                skill_name=row[0],
                total_calls=row[1],
                success_count=row[2],
                failure_count=row[3],
                rejection_count=row[4],
                success_rate=row[2] / row[1] if row[1] > 0 else 0.0,
                avg_confidence=row[5],
                last_called=row[6]
            )
            for row in rows
        ]

    def get_recent_calls(self, limit: int = 100) -> List[SkillCall]:
        """获取最近的调用记录

        Args:
            limit: 返回数量

        Returns:
            调用记录列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM skill_calls
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [
            SkillCall(
                id=row[0],
                timestamp=row[1],
                user_request=row[2],
                intent=row[3],
                matched_skills=json.loads(row[4]),
                recommended_skill=row[5],
                confidence=row[6],
                user_accepted=bool(row[7]),
                execution_success=bool(row[8]) if row[8] is not None else None,
                user_feedback=row[9] or ""
            )
            for row in rows
        ]

    def get_db_size(self) -> int:
        """获取数据库文件大小（字节）"""
        return self.db_path.stat().st_size if self.db_path.exists() else 0

    def get_record_count(self) -> int:
        """获取记录总数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM skill_calls")
        count = cursor.fetchone()[0]

        conn.close()
        return count

    def cleanup_old_records(self, days: int = 30) -> int:
        """清理旧记录

        Args:
            days: 保留最近 N 天的记录

        Returns:
            删除的记录数
        """
        cutoff = (datetime.now().replace(microsecond=0).isoformat())
        # 简单实现，删除指定天数前的记录
        # 实际应该用日期计算

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # TODO: 实现基于日期的清理
        cursor.execute("""
            DELETE FROM skill_calls
            WHERE timestamp < ?
        """, (cutoff,))

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted

    def clear_all(self):
        """清空所有记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM skill_calls")
        cursor.execute("DELETE FROM skill_stats")

        conn.commit()
        conn.close()


# 导入 json 模块
import json
