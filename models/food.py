"""
美食数据库模型
"""

from sqlalchemy import Column, String, Text, Float, Integer, DateTime, Boolean
from sqlalchemy.sql import func

from models.user import Base

class Food(Base):
    """美食表"""
    __tablename__ = "foods"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)        # 美食名称
    restaurant = Column(String(200))                               # 餐馆名称
    description = Column(Text)                                     # 描述
    category = Column(String(50), index=True)                      # 分类（川菜/粤菜/小吃等）
    price = Column(Float, default=0.0)                             # 价格
    rating = Column(Float, default=0.0)                            # 评分
    rating_count = Column(Integer, default=0)                      # 评分人数
    location = Column(String(200))                                 # 位置
    image_url = Column(String(500))                                # 图片
    tags = Column(String(500))                                     # 标签（逗号分隔，用于倒排索引）
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())