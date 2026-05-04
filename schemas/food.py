"""
美食数据验证模式
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FoodCreate(BaseModel):
    """创建美食请求"""
    name: str
    restaurant: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: float = 0.0
    rating: float = 0.0
    location: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[str] = None

class FoodResponse(BaseModel):
    """美食响应"""
    id: int
    name: str
    restaurant: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: float
    rating: float
    rating_count: int
    location: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True