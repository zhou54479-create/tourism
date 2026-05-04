"""
日记管理API - 集成哈夫曼压缩
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List
import json

from config import settings
from schemas.diary import DiaryCreate, DiaryResponse

router = APIRouter()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@router.post("/", response_model=DiaryResponse)
async def create_diary(data: DiaryCreate):
    """创建日记（自动哈夫曼压缩内容）"""
    from models.diary import Diary, Base
    from algorithms.huffman_compression import compress
    
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 压缩日记内容
        compressed_data, code_table = compress(data.content)
        
        # 编码表转为JSON字符串后存到compressed_content字段
        code_table_json = json.dumps(code_table, ensure_ascii=False)
        
        diary = Diary(
            user_id=1,
            title=data.title,
            content=data.content,              # 保留原文方便直接查询
            compressed_content=compressed_data, # 压缩后的二进制数据
            is_compressed=True,
            location=data.location,
            is_public=data.is_public
        )
        db.add(diary)
        db.commit()
        db.refresh(diary)
        
        # 给响应添加压缩信息
        diary.original_size = len(data.content.encode('utf-8'))
        diary.compressed_size = len(compressed_data)
        
        return diary
    finally:
        db.close()

@router.get("/", response_model=List[DiaryResponse])
async def list_diaries(skip: int = 0, limit: int = 10):
    """获取日记列表"""
    from models.diary import Diary
    
    db = SessionLocal()
    try:
        diaries = db.query(Diary).order_by(Diary.created_at.desc()).offset(skip).limit(limit).all()
        
        # 添加压缩信息
        for d in diaries:
            d.original_size = len(d.content.encode('utf-8'))
            d.compressed_size = len(d.compressed_content) if d.compressed_content else 0
        
        return diaries
    finally:
        db.close()

@router.get("/{diary_id}", response_model=DiaryResponse)
async def get_diary(diary_id: int):
    """获取单篇日记"""
    from models.diary import Diary
    
    db = SessionLocal()
    try:
        diary = db.query(Diary).filter(Diary.id == diary_id).first()
        if not diary:
            raise HTTPException(status_code=404, detail="日记不存在")
        
        diary.original_size = len(diary.content.encode('utf-8'))
        diary.compressed_size = len(diary.compressed_content) if diary.compressed_content else 0
        
        return diary
    finally:
        db.close()