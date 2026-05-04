"""
AIGC服务 - DeepSeek API
智能问答、行程规划、推荐
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from openai import OpenAI

from config import settings

router = APIRouter()

# DeepSeek 客户端（兼容OpenAI协议）
client = OpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url=settings.DEEPSEEK_BASE_URL
)

class ChatRequest(BaseModel):
    """聊天请求"""
    message: str
    history: Optional[List[dict]] = None  # 对话历史

class ChatResponse(BaseModel):
    """聊天响应"""
    reply: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """智能对话"""
    if not settings.DEEPSEEK_API_KEY:
        raise HTTPException(status_code=400, detail="未配置DeepSeek API Key")
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # 获取景点数据作为上下文
        from models.attraction import Attraction
        attractions = db.query(Attraction).filter(Attraction.is_active == True).all()
        
        # 获取美食数据
        from models.food import Food
        foods = db.query(Food).filter(Food.is_active == True).all()
        
        # 构建系统提示
        spot_list = "\n".join([
            f"- {a.name}（评分{a.rating}，价格{a.price}元，{a.location or '未知'}）"
            for a in attractions
        ])
        food_list = "\n".join([
            f"- {f.name}（评分{f.rating}，{f.restaurant or '未知'}，{f.location or '未知'}）"
            for f in foods
        ])
        
        system_prompt = f"""你是一个智能旅游助手，帮助用户规划旅行、推荐景点和美食。

当前数据库中的景点：
{spot_list or '暂无数据'}

当前数据库中的美食：
{food_list or '暂无数据'}

请根据以上数据回答用户问题，给出实用的建议。"""
        
        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        
        if request.history:
            messages.extend(request.history)
        
        messages.append({"role": "user", "content": request.message})
        
        # 调用 DeepSeek
        response = client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        reply = response.choices[0].message.content
        
        return ChatResponse(reply=reply)
    
    finally:
        db.close()

@router.post("/plan")
async def plan_trip(destination: str, days: int = 3, preferences: Optional[str] = None):
    """规划行程"""
    if not settings.DEEPSEEK_API_KEY:
        raise HTTPException(status_code=400, detail="未配置DeepSeek API Key")
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        from models.attraction import Attraction
        from models.food import Food
        
        attractions = db.query(Attraction).filter(Attraction.is_active == True).all()
        foods = db.query(Food).filter(Food.is_active == True).all()
        
        spot_list = "\n".join([f"- {a.name}（{a.location or ''}，评分{a.rating}）" for a in attractions])
        food_list = "\n".join([f"- {f.name}（{f.restaurant or ''}，{f.location or ''}）" for f in foods])
        
        prompt = f"""请为{destination}规划一个{days}天的旅游行程。
用户偏好：{preferences or '无特殊要求'}

可选景点：
{spot_list or '暂无数据'}

可选美食：
{food_list or '暂无数据'}

请给出详细的每日行程安排，包括景点参观顺序和用餐建议。"""
        
        response = client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=2000
        )
        
        return {"plan": response.choices[0].message.content}
    
    finally:
        db.close()