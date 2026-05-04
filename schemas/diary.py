"""
日记数据验证模式
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DiaryCreate(BaseModel):
    """创建日记请求"""
    title: str
    content: str
    location: Optional[str] = None
    is_public: bool = False

class DiaryResponse(BaseModel):
    """日记响应"""
    id: int
    user_id: int
    title: str
    content: str
    is_compressed: bool
    location: Optional[str] = None
    is_public: bool
    compressed_size: Optional[int] = None
    original_size: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True