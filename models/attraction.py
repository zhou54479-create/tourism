"""
景点数据库模型
"""

from sqlalchemy import Column, String, Float, Text, Integer, DateTime, Boolean
from sqlalchemy.sql import func

from models.user import Base

class Attraction(Base):
    """景点表"""
    __tablename__ = "attractions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)       # 景点名称
    description = Column(Text)                                    # 景点描述
    category = Column(String(50), index=True)                     # 分类（自然/人文/主题乐园等）
    price = Column(Float, default=0.0)                            # 门票价格
    rating = Column(Float, default=0.0)                           # 评分（1-5）
    rating_count = Column(Integer, default=0)                     # 评分人数
    location = Column(String(200))                                # 地理位置
    image_url = Column(String(500))                               # 图片URL
    is_active = Column(Boolean, default=True)                     # 是否上架
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())