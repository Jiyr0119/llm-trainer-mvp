# 中间件模块
import time
import uuid
import json
import logging
from typing import Callable, Dict, Any
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .errors import APIException, ErrorCode, InternalServerException

# 配置日志记录器
logger = logging.getLogger("llm-trainer")


class RequestIdMiddleware(BaseHTTPMiddleware):
    """请求ID中间件
    
    为每个请求生成唯一的请求ID，并在响应头中返回
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())
        # 将请求ID添加到请求状态中，以便在其他地方使用
        request.state.request_id = request_id
        
        # 记录请求信息
        logger.info(json.dumps({
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else None,
            "event": "request_start"
        }))
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 添加请求ID到响应头
            response.headers["X-Request-ID"] = request_id
            
            # 计算请求处理时间
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            # 记录响应信息
            logger.info(json.dumps({
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time": process_time,
                "event": "request_end"
            }))
            
            return response
        except Exception as e:
            # 计算请求处理时间
            process_time = time.time() - start_time
            
            # 记录异常信息
            logger.error(json.dumps({
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "error": str(e),
                "process_time": process_time,
                "event": "request_error"
            }), exc_info=True)
            
            # 重新抛出异常，由异常处理中间件处理
            raise


class ExceptionMiddleware(BaseHTTPMiddleware):
    """异常处理中间件
    
    统一处理API异常，返回标准格式的响应
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except APIException as e:
            # 处理自定义API异常
            return JSONResponse(
                status_code=e.status_code,
                content=e.to_dict()
            )
        except Exception as e:
            # 处理未捕获的异常
            logger.error(f"未捕获的异常: {str(e)}", exc_info=True)
            
            # 包装为内部服务器异常
            internal_error = InternalServerException(message=str(e))
            return JSONResponse(
                status_code=internal_error.status_code,
                content=internal_error.to_dict()
            )


def setup_middleware(app: FastAPI) -> None:
    """设置中间件
    
    Args:
        app: FastAPI应用实例
    """
    # 添加请求ID中间件
    app.add_middleware(RequestIdMiddleware)
    # 添加异常处理中间件
    app.add_middleware(ExceptionMiddleware)