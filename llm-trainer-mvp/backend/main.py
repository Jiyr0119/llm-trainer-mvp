# LLM Trainer MVP - FastAPI 应用主入口
# 重构后的main.py，使用模块化的服务层和API路由架构

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
import logging
import os
from datetime import datetime

# 导入数据库初始化
from app.db import init_db

# 导入配置
from app.core.config import settings, get_log_level

# 导入中间件和响应工具
from app.core.middleware import setup_middleware
from app.core.response import APIResponse
from app.core.decorators import standardized_response
from app.core.errors import APIException, ErrorCode
from app.core.logger import setup_logger
from app.core.exception_handler import setup_exception_handlers

# 导入API路由
from app.api import api_router

# 配置日志系统
LOG_PATH = settings.LOG_PATH
os.makedirs(LOG_PATH, exist_ok=True)

# 使用新的日志系统
logger = setup_logger(
    name="llm-trainer",
    log_file=os.path.join(LOG_PATH, "app.log"),
    level=get_log_level()
)

# 添加控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
logger.addHandler(console_handler)

# 确保必要的目录存在
UPLOAD_PATH = settings.UPLOAD_PATH
MODEL_PATH = settings.MODEL_PATH
os.makedirs(UPLOAD_PATH, exist_ok=True)
os.makedirs(MODEL_PATH, exist_ok=True)

# 初始化FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# 配置跨域资源共享(CORS)中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置自定义中间件（请求ID和异常处理）
setup_middleware(app)

# 配置全局异常处理器
setup_exception_handlers(app)

# 健康检查端点
@app.get("/", response_model=None, summary="根路径健康检查")
@standardized_response("API服务正常运行")
async def root():
    """根路径健康检查"""
    return {
        "message": "LLM Trainer MVP API",
        "version": settings.APP_VERSION,
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health", response_model=None, summary="健康检查")
@standardized_response("服务健康")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.APP_ENV
    }

# 注册API路由
app.include_router(api_router, prefix="/api")

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行的初始化操作"""
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"环境: {settings.APP_ENV}")
    logger.info(f"调试模式: {settings.DEBUG}")
    
    # 初始化数据库
    try:
        init_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise
    
    logger.info("应用启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行的清理操作"""
    logger.info("应用正在关闭...")
    
    # 清理模型缓存
    from app.services.prediction_service import prediction_service
    prediction_service.clear_cache()
    logger.info("模型缓存已清理")
    
    logger.info("应用已关闭")

# 应用运行入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.PORT,
        log_level="info",
        access_log=True
    )