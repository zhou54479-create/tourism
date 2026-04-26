"""
景点管理API
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List

from config import settings
from schemas.attraction import AttractionCreate, AttractionResponse

router = APIRouter()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@router.get("/", response_model=List[AttractionResponse])
async def list_attractions(skip: int = 0, limit: int = 10):
    """获取景点列表"""
    from models.attraction import Attraction
    
    db = SessionLocal()
    try:
        attractions = db.query(Attraction).filter(
            Attraction.is_active == True
        ).offset(skip).limit(limit).all()
        return attractions
    finally:
        db.close()

@router.post("/", response_model=AttractionResponse)
async def create_attraction(data: AttractionCreate):
    """创建景点"""
    from models.attraction import Attraction, Base
    
    # 确保表存在
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        attraction = Attraction(**data.model_dump())
        db.add(attraction)
        db.commit()
        db.refresh(attraction)
        return attraction
    finally:
        db.close()

@router.get("/top-rated", response_model=List[AttractionResponse])
async def top_rated_attractions(limit: int = 5):
    """获取评分最高的景点（堆排序推荐）"""
    from models.attraction import Attraction
    from algorithms.heap_sort import heap_sort
    
    db = SessionLocal()
    try:
        attractions = db.query(Attraction).filter(
            Attraction.is_active == True
        ).all()
        
        # 用堆排序按评分排序
        top = heap_sort(attractions, limit, key=lambda x: x.rating)
        return top
    finally:
        db.close()