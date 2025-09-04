# 健康检查API路由
from fastapi import APIRouter
from datetime import datetime

from ..core.response import APIResponse
from ..core.decorators import standardized_response
from ..schemas import HealthResponse
from ..core.config import settings

# 创建路由器
router = APIRouter(tags=["health"])


@router.get("/", response_model=HealthResponse)
@standardized_response("服务正常运行")
async def health_check():
    """
    健康检查接口
    
    返回服务状态和基本信息
    """
    return {
        "status": "healthy",
        "message": settings.APP_NAME,
        "timestamp": datetime.utcnow(),
        "version": settings.APP_VERSION
    }


@router.get("/health", response_model=HealthResponse)
@standardized_response("服务详细状态正常")
async def detailed_health_check():
    """
    详细健康检查接口
    
    返回更详细的服务状态信息
    """
    try:
        # 这里可以添加更多的健康检查逻辑
        # 例如检查数据库连接、外部服务状态等
        
        return {
            "status": "healthy",
            "message": f"{settings.APP_NAME} - {settings.APP_DESCRIPTION}",
            "timestamp": datetime.utcnow(),
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "debug": settings.DEBUG
        }
    except Exception as e:
        # 异常将由全局异常处理器处理
        raise