"""
数据同步API - 手动触发高德地图数据同步
"""

from fastapi import APIRouter
from typing import List, Optional

from config import settings
from fastapi import HTTPException

router = APIRouter()

@router.post("/sync")
async def trigger_sync(cities: Optional[List[str]] = None):
    """手动触发数据同步"""
    if not settings.AMAP_API_KEY:
        raise HTTPException(status_code=400, detail="未配置高德地图API Key")
    
    from services.sync_service import DataSyncService
    
    service = DataSyncService()
    result = service.sync_all(cities)
    
    return {
        "message": "同步完成",
        "新增景点": result["attractions"],
        "新增美食": result["foods"]
    }
