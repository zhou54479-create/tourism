"""
用户管理API - MySQL数据库版
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.auth import hash_password
from config import settings

router = APIRouter()

# 创建数据库连接
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class UserCreate(BaseModel):
    """创建用户请求"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """用户注册"""
    from models.user import User, Base
    
    # 确保表存在
    Base.metadata.create_all(bind=engine)
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 检查用户名和邮箱是否已存在
        existing = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing:
            if existing.username == user_data.username:
                raise HTTPException(status_code=400, detail="用户名已存在")
            else:
                raise HTTPException(status_code=400, detail="邮箱已被注册")
        
        # 创建新用户（密码暂时明文，后面再加密）
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),  # 加密存储
            full_name=user_data.full_name
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    finally:
        db.close()
@router.post("/login")
async def login(username: str, password: str):
    """用户登录"""
    from models.user import User
    
    db = SessionLocal()
    try:
        # 查找用户
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        
        # 验证密码
        from utils.auth import verify_password, create_access_token
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        
        # 生成令牌
        token = create_access_token({"sub": str(user.id)})
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name
            }
        }
    
    finally:
        db.close()