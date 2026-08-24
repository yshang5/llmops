"""
  @File    : jieba_service.py
  @Author  : Yue
  @Date    : 2026/8/18 19:00
  @Desc    : 
"""
import jieba
from injector import inject
from dataclasses import dataclass
from jieba.analyse import default_tfidf

from internal.entity.jieba_entity import STOPWORD_SET


@dataclass
@inject
class JiebaService:
    """结巴分词服务"""

    def __init__(self):
        """构造函数，扩展jieba的停用词"""
        default_tfidf.stop_words = STOPWORD_SET

    @classmethod
    def extract_keywords(cls, text: str, max_keyword_pre_chunk: int = 10) -> list[str]:
        """根据输入的文本，提供对应文本的关键词列表"""
        return jieba.analyse.extract_tags(
            sentence=text,
            topK=max_keyword_pre_chunk,
        )
