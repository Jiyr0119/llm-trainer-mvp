# API路由模块初始化文件
# 提供所有API路由的统一入口

from fastapi import APIRouter
from .datasets import router as datasets_router
from .training import router as training_router
from .prediction import router as prediction_router

# 创建主路由器
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(datasets_router, tags=["数据集管理"])
api_router.include_router(training_router, tags=["模型训练"])
api_router.include_router(prediction_router, tags=["模型预测"])

__all__ = ["api_router"]