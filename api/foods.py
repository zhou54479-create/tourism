"""
美食推荐API
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List

from config import settings
from schemas.food import FoodCreate, FoodResponse

router = APIRouter()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@router.post("/", response_model=FoodResponse)
async def create_food(data: FoodCreate):
    """创建美食"""
    from models.food import Food, Base
    
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        food = Food(**data.model_dump())
        db.add(food)
        db.commit()
        db.refresh(food)
        return food
    finally:
        db.close()

@router.get("/", response_model=List[FoodResponse])
async def list_foods(skip: int = 0, limit: int = 10):
    """获取美食列表"""
    from models.food import Food
    
    db = SessionLocal()
    try:
        foods = db.query(Food).filter(Food.is_active == True).offset(skip).limit(limit).all()
        return foods
    finally:
        db.close()

@router.get("/top-rated", response_model=List[FoodResponse])
async def top_rated_foods(limit: int = 5):
    """评分最高的美食（堆排序）"""
    from models.food import Food
    from algorithms.heap_sort import heap_sort
    
    db = SessionLocal()
    try:
        foods = db.query(Food).filter(Food.is_active == True).all()
        top = heap_sort(foods, limit, key=lambda x: x.rating)
        return top
    finally:
        db.close()

@router.get("/search", response_model=List[FoodResponse])
async def search_foods(keyword: str, limit: int = 10):
    """搜索美食（倒排索引）"""
    from models.food import Food
    from algorithms.inverted_index import InvertedIndex
    
    db = SessionLocal()
    try:
        foods = db.query(Food).filter(Food.is_active == True).all()
        
        # 建立倒排索引
        index = InvertedIndex()
        for food in foods:
            text = f"{food.name} {food.category} {food.tags or ''} {food.description or ''}"
            index.add_document(food.id, text)
        
        # 搜索
        results = index.search(keyword, limit)
        
        # 按搜索结果排序返回
        food_map = {f.id: f for f in foods}
        return [food_map[rid] for rid in results if rid in food_map]
    finally:
        db.close()