"""
全文检索API - 跨景点/美食/日记搜索
"""

from fastapi import APIRouter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
from pydantic import BaseModel

from config import settings

router = APIRouter()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class SearchResult(BaseModel):
    """搜索结果"""
    id: int
    type: str  # attraction / food / diary
    title: str
    content: str
    rating: Optional[float] = None

@router.get("/", response_model=List[SearchResult])
async def search_all(q: str, limit: int = 10):
    """
    全局搜索（KMP + 倒排索引）
    搜索景点、美食、日记的名称和描述
    """
    if not q:
        return []
    
    from algorithms.kmp_search import kmp_search
    from algorithms.inverted_index import InvertedIndex
    
    db = SessionLocal()
    try:
        results = []
        
        # ===== 搜索景点 =====
        from models.attraction import Attraction
        index = InvertedIndex()
        attractions = db.query(Attraction).filter(Attraction.is_active == True).all()
        for a in attractions:
            text = f"{a.name} {a.description or ''} {a.location or ''}"
            index.add_document(f"a_{a.id}", text)
        
        matched_ids = index.search(q, limit)
        for mid in matched_ids:
            a_id = int(mid.replace("a_", ""))
            a = next((x for x in attractions if x.id == a_id), None)
            if a:
                # 用KMP找到精确匹配位置
                search_text = f"{a.name} {a.description or ''}"
                pos = kmp_search(search_text, q)
                if pos:
                    results.append(SearchResult(
                        id=a.id, type="attraction", title=a.name,
                        content=a.description or "", rating=a.rating
                    ))
        
        # ===== 搜索美食 =====
        from models.food import Food
        index2 = InvertedIndex()
        foods = db.query(Food).filter(Food.is_active == True).all()
        for f in foods:
            text = f"{f.name} {f.tags or ''} {f.description or ''}"
            index2.add_document(f"f_{f.id}", text)
        
        matched_ids = index2.search(q, limit)
        for mid in matched_ids:
            f_id = int(mid.replace("f_", ""))
            f = next((x for x in foods if x.id == f_id), None)
            if f:
                results.append(SearchResult(
                    id=f.id, type="food", title=f.name,
                    content=f.description or "", rating=f.rating
                ))
        
        # ===== 搜索日记 =====
        from models.diary import Diary
        index3 = InvertedIndex()
        diaries = db.query(Diary).filter(Diary.is_public == True).all()
        for d in diaries:
            text = f"{d.title} {d.content} {d.location or ''}"
            index3.add_document(f"d_{d.id}", text)
        
        matched_ids = index3.search(q, limit)
        for mid in matched_ids:
            d_id = int(mid.replace("d_", ""))
            d = next((x for x in diaries if x.id == d_id), None)
            if d:
                results.append(SearchResult(
                    id=d.id, type="diary", title=d.title,
                    content=d.content[:100] + "...", rating=None
                ))
        
        return results[:limit]
    finally:
        db.close()