"""
Embedding 模型封装

支持中英双语的文本 embedding，使用 sentence-transformers
"""

from functools import lru_cache
from typing import List, Union
import numpy as np


class EmbeddingModel:
    """文本 Embedding 模型"""

    # 默认模型：支持中英双语的轻量级模型
    DEFAULT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

    def __init__(self, model_name: str = DEFAULT_MODEL, device: str = "cpu"):
        """初始化 Embedding 模型

        Args:
            model_name: 模型名称，默认使用多语言模型
            device: 运行设备，"cpu" 或 "cuda"
        """
        self.model_name = model_name
        self.device = device
        self._model = None
        self._load_model()

    def _load_model(self):
        """延迟加载模型"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name, device=self.device)
            except ImportError:
                raise ImportError(
                    "sentence-transformers 未安装，请运行: pip install sentence-transformers"
                )

    def encode(
        self,
        texts: Union[str, List[str]],
        normalize: bool = True,
        batch_size: int = 32
    ) -> np.ndarray:
        """将文本编码为向量

        Args:
            texts: 单个文本或文本列表
            normalize: 是否归一化向量
            batch_size: 批处理大小

        Returns:
            向量数组，形状为 (num_texts, embedding_dim)
        """
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self._model.encode(
            texts,
            normalize_embeddings=normalize,
            batch_size=batch_size,
            show_progress_bar=False
        )

        return embeddings

    def similarity(self, text1: Union[str, np.ndarray], text2: Union[str, np.ndarray]) -> float:
        """计算两个文本的相似度

        Args:
            text1: 文本或向量
            text2: 文本或向量

        Returns:
            相似度分数 [0, 1]
        """
        vec1 = self.encode(text1) if isinstance(text1, str) else text1
        vec2 = self.encode(text2) if isinstance(text2, str) else text2

        # 余弦相似度
        return float(np.dot(vec1, vec2.T).flatten()[0])

    def similarities(
        self,
        query: Union[str, np.ndarray],
        candidates: List[str]
    ) -> List[float]:
        """计算查询与多个候选文本的相似度

        Args:
            query: 查询文本或向量
            candidates: 候选文本列表

        Returns:
            相似度分数列表
        """
        query_vec = self.encode(query) if isinstance(query, str) else query
        candidate_vecs = self.encode(candidates)

        # 批量计算余弦相似度
        similarities = np.dot(candidate_vecs, query_vec.T).flatten()
        return similarities.tolist()

    @property
    def dimension(self) -> int:
        """返回向量维度"""
        return self._model.get_sentence_embedding_dimension()

    @staticmethod
    @lru_cache(maxsize=1)
    def get_default() -> "EmbeddingModel":
        """获取默认的单例模型"""
        return EmbeddingModel()


# 便捷函数
def encode_text(text: str, model: EmbeddingModel = None) -> np.ndarray:
    """便捷函数：编码单个文本"""
    if model is None:
        model = EmbeddingModel.get_default()
    return model.encode(text)[0]


def compute_similarity(text1: str, text2: str, model: EmbeddingModel = None) -> float:
    """便捷函数：计算两个文本的相似度"""
    if model is None:
        model = EmbeddingModel.get_default()
    return model.similarity(text1, text2)
