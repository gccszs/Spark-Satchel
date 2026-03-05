"""
意图分析模块

从用户请求中提取意图，支持关键词匹配和语义分析
"""

import re
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Intent:
    """用户意图"""
    primary: str           # 主要意图
    keywords: List[str]    # 提取的关键词
    entities: List[str]    # 实体（如文件名、格式等）
    confidence: float      # 意图识别置信度


class IntentAnalyzer:
    """意图分析器"""

    # 常见意图模式
    INTENT_PATTERNS = {
        "document_process": [
            r"处理.*文档", r"处理.*文件", r"转换.*格式",
            r"处理.*PDF", r"处理.*Word", r"处理.*Excel",
            r"extract.*document", r"process.*file"
        ],
        "project_create": [
            r"创建.*项目", r"初始化.*项目", r"新建.*项目",
            r"based on.*create", r"template.*project"
        ],
        "data_analysis": [
            r"分析.*数据", r"处理.*数据", r"统计.*",
            r"analyze.*data", r"process.*data"
        ],
        "search_skill": [
            r"查找.*技能", r"搜索.*技能", r"什么.*技能",
            r"find.*skill", r"search.*skill"
        ],
        "disk_clean": [
            r"清理.*磁盘", r"清理.*空间", r"删除.*缓存",
            r"clean.*disk", r"free.*space"
        ],
        "ai_collaborate": [
            r"多.*AI.*协作", r"AI.*协同", r"Agent.*协作",
            r"multi.*agent", r"AI.*collaborate"
        ]
    }

    # 实体提取模式
    ENTITY_PATTERNS = {
        "file_format": [
            r"\.(PDF|pdf|DOCX|docx|PPT|ppt|XLSX|xlsx|CSV|csv)",
            r"(PDF|Word|Excel|PowerPoint|文档|表格)"
        ],
        "programming_language": [
            r"\b(Python|Java|JavaScript|TypeScript|Go|Rust|C\+\+)\b"
        ]
    }

    def __init__(self):
        """初始化意图分析器"""
        self._compile_patterns()

    def _compile_patterns(self):
        """编译正则表达式"""
        self.compiled_intents = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            self.compiled_intents[intent] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

        self.compiled_entities = {}
        for entity_type, patterns in self.ENTITY_PATTERNS.items():
            self.compiled_entities[entity_type] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def analyze(self, user_request: str) -> Intent:
        """分析用户请求的意图

        Args:
            user_request: 用户请求文本

        Returns:
            意图对象
        """
        keywords = self._extract_keywords(user_request)
        entities = self._extract_entities(user_request)
        primary_intent = self._match_intent(user_request)
        confidence = self._calculate_confidence(user_request, primary_intent)

        return Intent(
            primary=primary_intent,
            keywords=keywords,
            entities=entities,
            confidence=confidence
        )

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词

        Args:
            text: 输入文本

        Returns:
            关键词列表
        """
        # 简单实现：提取中文词汇和英文单词
        # 实际应该使用 jieba 或其他分词工具

        # 移除标点符号
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)

        # 提取中文词汇（2-4字）
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)

        # 提取英文单词
        english_words = re.findall(r'\b[a-zA-Z]{3,}\b', text)

        # 过滤常见词
        stop_words = {'这个', '那个', '可以', '需要', 'the', 'a', 'an', 'is', 'are'}
        keywords = [w for w in chinese_words + english_words if w.lower() not in stop_words]

        return list(set(keywords))

    def _extract_entities(self, text: str) -> List[str]:
        """提取实体

        Args:
            text: 输入文本

        Returns:
            实体列表
        """
        entities = []

        for entity_type, patterns in self.compiled_entities.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                entities.extend(matches)

        return list(set(entities))

    def _match_intent(self, text: str) -> str:
        """匹配意图

        Args:
            text: 输入文本

        Returns:
            意图名称
        """
        best_intent = "general"
        best_score = 0

        for intent, patterns in self.compiled_intents.items():
            score = sum(1 for p in patterns if p.search(text))
            if score > best_score:
                best_score = score
                best_intent = intent

        return best_intent

    def _calculate_confidence(self, text: str, intent: str) -> float:
        """计算意图识别置信度

        Args:
            text: 输入文本
            intent: 匹配的意图

        Returns:
            置信度 [0, 1]
        """
        # 基于匹配模式数量
        patterns = self.compiled_intents.get(intent, [])
        match_count = sum(1 for p in patterns if p.search(text))

        if match_count == 0:
            return 0.3  # 默认置信度

        # 匹配越多，置信度越高
        confidence = min(0.5 + match_count * 0.15, 1.0)
        return confidence

    def extract_skill_hints(self, user_request: str) -> List[str]:
        """从请求中提取技能提示

        Args:
            user_request: 用户请求

        Returns:
            可能的技能名称列表
        """
        hints = []

        # 直接提到的技能名
        skill_names = re.findall(
            r'(\w+-?\w*\s*skill)',
            user_request,
            re.IGNORECASE
        )
        hints.extend([s.strip().lower() for s in skill_names])

        # 常见功能映射
        function_mapping = {
            "pdf": ["pdf-skill"],
            "文档": ["pdf-skill", "docx-skill"],
            "word": ["docx-skill"],
            "excel": ["xlsx-skill"],
            "表格": ["xlsx-skill"],
            "ppt": ["pptx-skill"],
            "演示": ["pptx-skill"],
            "清理": ["disk-cleaner"],
            "磁盘": ["disk-cleaner"],
            "协作": ["agent-call"],
            "项目": ["project-start-skill"]
        }

        for keyword, skills in function_mapping.items():
            if keyword.lower() in user_request.lower():
                hints.extend(skills)

        return list(set(hints))
