"""
向量数据库层

使用 ChromaDB 进行向量存储和检索，支持分库策略
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class SkillCategory(Enum):
    """技能分类"""
    DOCUMENT = "document"       # 文档处理类
    AI_TOOLS = "ai_tools"      # AI 工具类
    DEV = "dev"                # 开发工具类
    UTILITY = "utility"        # 通用工具类


# 分类映射
CATEGORY_MAPPING = {
    "document": ["pdf", "docx", "pptx", "xlsx"],
    "ai_tools": ["agent-call", "autogpt-agents", "brainstorming"],
    "dev": ["skill-creator", "skill-lookup", "git-worktrees"],
    "utility": ["disk-cleaner", "work-log", "humanizer"]
}


@dataclass
class SkillMetadata:
    """技能元数据"""
    name: str
    path: str
    description: str
    tags: List[str]
    trigger_keywords: List[str]
    category: str
    version: str = "1.0.0"
    file_hash: str = ""
    installed_at: str = ""
    last_updated: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillMetadata":
        return cls(**data)


@dataclass
class SearchResult:
    """搜索结果"""
    skill_name: str
    similarity: float
    metadata: SkillMetadata
    confidence: float = 0.0


class VectorStore:
    """向量存储管理器"""

    def __init__(
        self,
        persist_directory: str = None,
        embedding_model=None
    ):
        """初始化向量存储

        Args:
            persist_directory: 持久化目录
            embedding_model: Embedding 模型实例
        """
        if persist_directory is None:
            persist_directory = os.path.join(
                os.path.dirname(__file__),
                "..", "..", "data", "collections"
            )

        self.persist_dir = Path(persist_directory)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.embedding_model = embedding_model
        self._client = None
        self._collections = {}

        self._init_client()

    def _init_client(self):
        """初始化 ChromaDB 客户端"""
        try:
            import chromadb
            self._client = chromadb.PersistentClient(path=str(self.persist_dir))
        except ImportError:
            raise ImportError(
                "chromadb 未安装，请运行: pip install chromadb"
            )

    def _get_collection_name(self, category: str) -> str:
        """获取集合名称"""
        return f"skills_{category}"

    def _get_or_create_collection(self, category: str):
        """获取或创建集合"""
        if category not in self._collections:
            collection_name = self._get_collection_name(category)
            self._collections[category] = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"category": category}
            )
        return self._collections[category]

    def add_skill(self, metadata: SkillMetadata):
        """添加技能到向量库

        Args:
            metadata: 技能元数据
        """
        # 生成 embedding
        text = self._prepare_skill_text(metadata)
        if self.embedding_model:
            embedding = self.embedding_model.encode(text)[0].tolist()
        else:
            embedding = None

        # 添加到对应分类的集合
        collection = self._get_or_create_collection(metadata.category)

        collection.add(
            documents=[text],
            embeddings=[embedding] if embedding else None,
            metadatas=[metadata.to_dict()],
            ids=[metadata.name]
        )

    def _prepare_skill_text(self, metadata: SkillMetadata) -> str:
        """准备用于检索的文本"""
        parts = [
            metadata.name,
            metadata.description,
            " ".join(metadata.tags),
            " ".join(metadata.trigger_keywords)
        ]
        return " ".join(parts)

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 5,
        min_similarity: float = 0.3
    ) -> List[SearchResult]:
        """搜索技能

        Args:
            query: 查询文本
            category: 限制分类，None 表示搜索所有分类
            top_k: 返回结果数量
            min_similarity: 最小相似度阈值

        Returns:
            搜索结果列表
        """
        if self.embedding_model:
            query_embedding = self.embedding_model.encode(query)[0].tolist()
        else:
            query_embedding = None

        results = []

        # 确定要搜索的分类
        if category:
            categories = [category]
        else:
            categories = [c.value for c in SkillCategory]

        # 搜索每个分类
        for cat in categories:
            try:
                collection = self._get_or_create_collection(cat)
                search_results = collection.query(
                    query_embeddings=[query_embedding] if query_embedding else None,
                    query_texts=[query] if not query_embedding else None,
                    n_results=top_k
                )

                if search_results and search_results["ids"][0]:
                    for i, skill_id in enumerate(search_results["ids"][0]):
                        similarity = search_results["distances"][0][i] if query_embedding else 0.5
                        # 转换距离为相似度
                        if query_embedding:
                            similarity = 1 - similarity

                        if similarity >= min_similarity:
                            metadata = SkillMetadata.from_dict(
                                search_results["metadatas"][0][i]
                            )
                            results.append(SearchResult(
                                skill_name=skill_id,
                                similarity=similarity,
                                metadata=metadata,
                                confidence=similarity
                            ))
            except Exception as e:
                # 集合可能不存在，跳过
                continue

        # 按相似度排序
        results.sort(key=lambda x: x.similarity, reverse=True)
        return results[:top_k]

    def remove_skill(self, skill_name: str, category: str):
        """从向量库移除技能

        Args:
            skill_name: 技能名称
            category: 技能分类
        """
        collection = self._get_or_create_collection(category)
        collection.delete(ids=[skill_name])

    def get_skill_count(self, category: Optional[str] = None) -> Dict[str, int]:
        """获取技能数量

        Args:
            category: 分类，None 表示获取所有分类

        Returns:
            分类 -> 技能数量的映射
        """
        counts = {}
        categories = [category] if category else [c.value for c in SkillCategory]

        for cat in categories:
            try:
                collection = self._get_or_create_collection(cat)
                counts[cat] = collection.count()
            except:
                counts[cat] = 0

        return counts

    def clear_all(self):
        """清空所有数据"""
        for cat in SkillCategory:
            try:
                collection = self._get_or_create_collection(cat.value)
                self._client.delete_collection(collection.name)
            except:
                pass
        self._collections.clear()
