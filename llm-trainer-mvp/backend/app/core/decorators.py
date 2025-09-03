# API响应装饰器模块
from functools import wraps
from typing import Any, Callable, Union
from fastapi.responses import JSONResponse

from .response import APIResponse
from .errors import APIException, InternalServerException
from .logger import setup_logger

logger = setup_logger(__name__)


def standardized_response(
    success_message: str = "操作成功",
    success_code: int = 200
):
    """标准化API响应装饰器
    
    用于统一API接口的响应格式，自动处理异常和响应包装
    
    Args:
        success_message: 成功时的默认消息
        success_code: 成功时的响应码
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Union[dict, JSONResponse]:
            try:
                # 执行原函数
                result = await func(*args, **kwargs)
                
                # 检查结果是否已经是标准格式
                if isinstance(result, dict) and 'success' in result:
                    return result  # 已经是标准格式，直接返回
                elif isinstance(result, JSONResponse):
                    return result  # 已经是JSONResponse，直接返回
                else:
                    # 包装为标准成功响应
                    return APIResponse.success(
                        data=result,
                        message=success_message,
                        code=success_code
                    )
                    
            except APIException as e:
                # API异常直接抛出，由异常处理器处理
                raise e
                
            except Exception as e:
                # 其他异常转换为内部服务器错误
                logger.error(f"函数 {func.__name__} 执行失败: {str(e)}", exc_info=True)
                raise InternalServerException(message=f"服务器内部错误: {str(e)}")
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Union[dict, JSONResponse]:
            try:
                # 执行原函数
                result = func(*args, **kwargs)
                
                # 检查结果是否已经是标准格式
                if isinstance(result, dict) and 'success' in result:
                    return result  # 已经是标准格式，直接返回
                elif isinstance(result, JSONResponse):
                    return result  # 已经是JSONResponse，直接返回
                else:
                    # 包装为标准成功响应
                    return APIResponse.success(
                        data=result,
                        message=success_message,
                        code=success_code
                    )
                    
            except APIException as e:
                # API异常直接抛出，由异常处理器处理
                raise e
                
            except Exception as e:
                # 其他异常转换为内部服务器错误
                logger.error(f"函数 {func.__name__} 执行失败: {str(e)}", exc_info=True)
                raise InternalServerException(message=f"服务器内部错误: {str(e)}")
        
        # 根据函数是否为协程选择合适的包装器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


def api_route(
    success_message: str = "操作成功",
    success_code: int = 200,
    auto_catch_exceptions: bool = True
):
    """API路由装饰器
    
    结合了标准化响应和额外的API路由功能
    
    Args:
        success_message: 成功时的默认消息
        success_code: 成功时的响应码
        auto_catch_exceptions: 是否自动捕获异常
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        if auto_catch_exceptions:
            # 应用标准化响应装饰器
            func = standardized_response(success_message, success_code)(func)
        
        # 可以在这里添加其他API路由相关的功能
        # 例如：认证检查、权限验证、请求日志等
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 记录API调用日志
            logger.info(f"API调用: {func.__name__}")
            return await func(*args, **kwargs)
            
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 记录API调用日志
            logger.info(f"API调用: {func.__name__}")
            return func(*args, **kwargs)
        
        # 根据函数是否为协程选择合适的包装器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


def validate_and_respond(
    success_message: str = "操作成功",
    error_message: str = "操作失败"
):
    """验证并响应装饰器
    
    用于需要特殊验证逻辑的API接口
    
    Args:
        success_message: 成功时的消息
        error_message: 失败时的消息
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                
                # 检查结果的有效性
                if result is None:
                    return APIResponse.error(message=error_message)
                elif isinstance(result, bool) and not result:
                    return APIResponse.error(message=error_message)
                elif isinstance(result, dict) and 'success' in result:
                    return result
                else:
                    return APIResponse.success(data=result, message=success_message)
                    
            except APIException as e:
                raise e
            except Exception as e:
                logger.error(f"验证函数 {func.__name__} 执行失败: {str(e)}", exc_info=True)
                raise InternalServerException(message=f"验证失败: {str(e)}")
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                # 检查结果的有效性
                if result is None:
                    return APIResponse.error(message=error_message)
                elif isinstance(result, bool) and not result:
                    return APIResponse.error(message=error_message)
                elif isinstance(result, dict) and 'success' in result:
                    return result
                else:
                    return APIResponse.success(data=result, message=success_message)
                    
            except APIException as e:
                raise e
            except Exception as e:
                logger.error(f"验证函数 {func.__name__} 执行失败: {str(e)}", exc_info=True)
                raise InternalServerException(message=f"验证失败: {str(e)}")
        
        # 根据函数是否为协程选择合适的包装器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator