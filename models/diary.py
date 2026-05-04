"""
日记数据库模型
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, LargeBinary
from sqlalchemy.sql import func

from models.user import Base

class Diary(Base):
    """日记表"""
    __tablename__ = "diaries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)  # 所属用户
    title = Column(String(200), nullable=False)             # 日记标题
    content = Column(Text, nullable=False)                  # 日记内容（原始文本）
    compressed_content = Column(LargeBinary, nullable=True) # 哈夫曼压缩后的内容
    is_compressed = Column(Boolean, default=False)          # 是否已压缩
    location = Column(String(200))                          # 记录地点
    is_public = Column(Boolean, default=False)              # 是否公开
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())