"""
智能旅游系统 - 主入口文件
功能模块：旅游推荐 + 日记管理 + 美食推荐 + 全文检索 + 压缩 + AIGC
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import logging
import os

from config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    - 启动时：初始化资源
    - 关闭时：清理资源
    """
    # 启动时
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    
    # 创建必要的目录
    import os
    os.makedirs("logs", exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)  # 确保上传目录存在
    
    logger.info(f"✅ 应用初始化完成 (DEBUG={settings.DEBUG})")
    logger.info(f"📁 上传目录: {os.path.abspath(settings.UPLOAD_DIR)}")
    
    yield  # 应用运行
    
    # 关闭时
    logger.info("🛑 智能旅游系统关闭中...")
    logger.info("✅ 资源清理完成")

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    description="智能旅游系统后端服务，包含旅游推荐、日记管理、美食推荐、全文检索、压缩和AIGC功能",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [
        "http://localhost:3000",
        "https://your-frontend-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件（用于上传的文件访问）
# app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 导入路由模块（先创建占位，后面再实现）
from api.users import router as users_router
from api.attractions import router as attractions_router

# 注册路由（先注释掉，等创建了api模块再取消注释）
app.include_router(users_router, prefix="/api/users", tags=["用户管理"])
app.include_router(attractions_router, prefix="/api/attractions", tags=["景点管理"])
# app.include_router(diaries.router, prefix="/api/diaries", tags=["旅游日记"])
# app.include_router(foods.router, prefix="/api/foods", tags=["美食推荐"])
# app.include_router(search.router, prefix="/api/search", tags=["全文检索"])
# app.include_router(compression.router, prefix="/api/compression", tags=["数据压缩"])
# app.include_router(aigc.router, prefix="/api/aigc", tags=["AIGC服务"])

# 健康检查端点
@app.get("/")
async def root():
    """根端点，返回服务状态"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": "development" if settings.DEBUG else "production",
        "modules": [
            {"name": "旅游推荐", "endpoint": "/api/attractions"},
            {"name": "日记管理", "endpoint": "/api/diaries"},
            {"name": "美食推荐", "endpoint": "/api/foods"},
            {"name": "全文检索", "endpoint": "/api/search"},
            {"name": "数据压缩", "endpoint": "/api/compression"},
            {"name": "AIGC服务", "endpoint": "/api/aigc"}
        ],
        "documentation": "/docs" if settings.DEBUG else None
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": "2026-04-19T14:33:00Z",
        "service": "smart-travel-system",
        "version": settings.APP_VERSION
    }

# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "服务器内部错误"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )