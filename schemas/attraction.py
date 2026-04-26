"""
景点数据验证模式
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AttractionCreate(BaseModel):
    """创建景点请求"""
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: float = 0.0
    rating: float = 0.0
    location: Optional[str] = None
    image_url: Optional[str] = None

class AttractionResponse(BaseModel):
    """景点响应"""
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: float
    rating: float
    rating_count: int
    location: Optional[str] = None
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True