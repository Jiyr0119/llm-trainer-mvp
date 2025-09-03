# 全局异常处理中间件
from typing import Union
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .errors import APIException, ErrorCode, InternalServerException
from .response import APIResponse
from .logger import setup_logger

logger = setup_logger(__name__)


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """API异常处理器
    
    Args:
        request: 请求对象
        exc: API异常
        
    Returns:
        标准格式的错误响应
    """
    logger.error(f"API异常: {exc.message}, 错误码: {exc.error_code.code}, 路径: {request.url}")
    
    return APIResponse.json_response(
        success=False,
        message=exc.message,
        code=exc.error_code.code,
        data=exc.data,
        status_code=exc.status_code
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """HTTP异常处理器
    
    Args:
        request: 请求对象
        exc: HTTP异常
        
    Returns:
        标准格式的错误响应
    """
    logger.error(f"HTTP异常: {exc.detail}, 状态码: {exc.status_code}, 路径: {request.url}")
    
    # 将HTTP异常转换为标准API响应格式
    error_code_map = {
        400: ErrorCode.INVALID_PARAMS,
        401: ErrorCode.PERMISSION_DENIED,
        403: ErrorCode.PERMISSION_DENIED,
        404: ErrorCode.RESOURCE_NOT_FOUND,
        408: ErrorCode.REQUEST_TIMEOUT,
        500: ErrorCode.INTERNAL_SERVER_ERROR,
    }
    
    error_code = error_code_map.get(exc.status_code, ErrorCode.UNKNOWN_ERROR)
    message = str(exc.detail) if exc.detail else error_code.message
    
    return APIResponse.json_response(
        success=False,
        message=message,
        code=error_code.code,
        status_code=exc.status_code
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """请求验证异常处理器
    
    Args:
        request: 请求对象
        exc: 请求验证异常
        
    Returns:
        标准格式的错误响应
    """
    logger.error(f"请求验证失败: {exc.errors()}, 路径: {request.url}")
    
    # 格式化验证错误信息
    error_details = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        msg = error["msg"]
        error_details.append(f"{field}: {msg}")
    
    error_message = "请求参数验证失败: " + "; ".join(error_details)
    
    return APIResponse.json_response(
        success=False,
        message=error_message,
        code=ErrorCode.INVALID_PARAMS.code,
        data={"validation_errors": exc.errors()},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器
    
    Args:
        request: 请求对象
        exc: 通用异常
        
    Returns:
        标准格式的错误响应
    """
    logger.error(f"未处理的异常: {str(exc)}, 类型: {type(exc).__name__}, 路径: {request.url}", exc_info=True)
    
    # 创建内部服务器错误异常
    internal_exc = InternalServerException(message=f"服务器内部错误: {str(exc)}")
    
    return APIResponse.json_response(
        success=False,
        message=internal_exc.message,
        code=internal_exc.error_code.code,
        status_code=internal_exc.status_code
    )


def setup_exception_handlers(app):
    """配置全局异常处理器
    
    Args:
        app: FastAPI应用实例
    """
    # API异常处理
    app.add_exception_handler(APIException, api_exception_handler)
    
    # HTTP异常处理
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # 请求验证异常处理
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # 通用异常处理（必须放在最后）
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("全局异常处理器配置完成")