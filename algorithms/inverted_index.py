"""
倒排索引算法 - 用于全文搜索
"""

from typing import Dict, List, Set
from collections import defaultdict
import re

class InvertedIndex:
    """倒排索引"""
    
    def __init__(self):
        self.index: Dict[str, Set[int]] = defaultdict(set)  # 词 -> 文档ID集合
        self.doc_count = 0
    
    def _tokenize(self, text: str) -> List[str]:
        """分词（简单中文分词，按字/词拆分）"""
        # 先按标点符号和空格拆分
        words = re.split(r'[\s,，。！？、；：""''（）()\.\!\?\;\:\'\"\(\)]+', text)
        result = []
        for word in words:
            if word:
                result.append(word)
        return result
    
    def add_document(self, doc_id: int, text: str):
        """添加文档到索引"""
        words = self._tokenize(text)
        for word in set(words):  # 去重
            self.index[word].add(doc_id)
        self.doc_count += 1
    
    def search(self, query: str, limit: int = 10) -> List[int]:
        """搜索，返回匹配的文档ID列表"""
        words = self._tokenize(query)
        if not words:
            return []
        
        # 取所有搜索词的交集（包含所有关键词的文档）
        result: Set[int] = None
        for word in words:
            if word in self.index:
                if result is None:
                    result = self.index[word].copy()
                else:
                    result &= self.index[word]
        
        if result is None:
            return []
        
        return sorted(result)[:limit]

    def add_documents_batch(self, docs: Dict[int, str]):
        """批量添加文档"""
        for doc_id, text in docs.items():
            self.add_document(doc_id, text)