# 响应工具模块
from typing import Any, Dict, Optional, Union
from fastapi.responses import JSONResponse


class APIResponse:
    """API响应工具类
    
    用于生成标准格式的API响应
    """
    @staticmethod
    def success(data: Any = None, message: str = "操作成功", code: int = 200) -> Dict[str, Any]:
        """成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            code: 响应码
            
        Returns:
            标准格式的成功响应
        """
        return {
            "success": True,
            "code": code,
            "message": message,
            "data": data
        }
    
    @staticmethod
    def error(message: str = "操作失败", code: int = 400, data: Any = None) -> Dict[str, Any]:
        """错误响应
        
        Args:
            message: 错误消息
            code: 错误码
            data: 错误数据
            
        Returns:
            标准格式的错误响应
        """
        return {
            "success": False,
            "code": code,
            "message": message,
            "data": data
        }
    
    @staticmethod
    def response(success: bool = True, message: str = "", code: int = 200, data: Any = None) -> Dict[str, Any]:
        """自定义响应
        
        Args:
            success: 是否成功
            message: 响应消息
            code: 响应码
            data: 响应数据
            
        Returns:
            标准格式的响应
        """
        return {
            "success": success,
            "code": code,
            "message": message,
            "data": data
        }
    
    @staticmethod
    def json_response(
        success: bool = True, 
        message: str = "", 
        code: int = 200, 
        data: Any = None, 
        status_code: Optional[int] = None
    ) -> JSONResponse:
        """JSON响应
        
        Args:
            success: 是否成功
            message: 响应消息
            code: 响应码
            data: 响应数据
            status_code: HTTP状态码，默认与code相同
            
        Returns:
            JSONResponse实例
        """
        content = {
            "success": success,
            "code": code,
            "message": message,
            "data": data
        }
        
        # 如果未指定HTTP状态码，则使用code
        if status_code is None:
            # 对于成功响应，使用200
            # 对于错误响应，使用code对应的HTTP状态码，如果code不是标准HTTP状态码，则使用400
            if success:
                status_code = 200
            else:
                # 常见HTTP错误码
                if code in [400, 401, 403, 404, 405, 408, 409, 429, 500, 501, 502, 503, 504]:
                    status_code = code
                else:
                    status_code = 400
        
        return JSONResponse(content=content, status_code=status_code)