# 错误码定义模块
from enum import Enum
from typing import Dict, Any, Optional
from fastapi import HTTPException
from fastapi.responses import JSONResponse


class ErrorCode(Enum):
    """错误码枚举类
    
    错误码规则：
    - 10xxx: 通用错误
    - 20xxx: 数据集相关错误
    - 30xxx: 训练相关错误
    - 40xxx: 模型和预测相关错误
    - 50xxx: 系统和服务错误
    """
    # 通用错误 (10xxx)
    UNKNOWN_ERROR = (10000, "未知错误")
    INVALID_PARAMS = (10001, "无效的参数")
    RESOURCE_NOT_FOUND = (10002, "资源不存在")
    PERMISSION_DENIED = (10003, "权限不足")
    REQUEST_TIMEOUT = (10004, "请求超时")
    
    # 数据集相关错误 (20xxx)
    DATASET_NOT_FOUND = (20001, "数据集不存在")
    DATASET_FORMAT_ERROR = (20002, "数据集格式错误")
    DATASET_UPLOAD_FAILED = (20003, "数据集上传失败")
    DATASET_PARSE_ERROR = (20004, "数据集解析错误")
    
    # 训练相关错误 (30xxx)
    TRAINING_FAILED = (30001, "训练失败")
    TRAINING_NOT_FOUND = (30002, "训练任务不存在")
    TRAINING_ALREADY_RUNNING = (30003, "训练任务已在运行")
    TRAINING_STOP_FAILED = (30004, "停止训练失败")
    
    # 模型和预测相关错误 (40xxx)
    MODEL_NOT_FOUND = (40001, "模型不存在")
    MODEL_LOAD_FAILED = (40002, "模型加载失败")
    PREDICTION_FAILED = (40003, "预测失败")
    
    # 系统和服务错误 (50xxx)
    DATABASE_ERROR = (50001, "数据库错误")
    FILE_SYSTEM_ERROR = (50002, "文件系统错误")
    SERVICE_UNAVAILABLE = (50003, "服务不可用")
    INTERNAL_SERVER_ERROR = (50004, "服务器内部错误")
    
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


class APIException(Exception):
    """API异常基类"""
    def __init__(
        self, 
        error_code: ErrorCode, 
        message: Optional[str] = None, 
        data: Any = None,
        status_code: int = 400
    ):
        self.error_code = error_code
        self.message = message or error_code.message
        self.data = data
        self.status_code = status_code
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "success": False,
            "code": self.error_code.code,
            "message": self.message,
            "data": self.data
        }


# 具体异常类定义
class ResourceNotFoundException(APIException):
    """资源不存在异常"""
    def __init__(self, message: Optional[str] = None, data: Any = None):
        super().__init__(
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            message=message,
            data=data,
            status_code=404
        )


class InvalidParamsException(APIException):
    """参数无效异常"""
    def __init__(self, message: Optional[str] = None, data: Any = None):
        super().__init__(
            error_code=ErrorCode.INVALID_PARAMS,
            message=message,
            data=data,
            status_code=400
        )


class DatasetNotFoundException(APIException):
    """数据集不存在异常"""
    def __init__(self, message: Optional[str] = None, data: Any = None):
        super().__init__(
            error_code=ErrorCode.DATASET_NOT_FOUND,
            message=message,
            data=data,
            status_code=404
        )


class TrainingNotFoundException(APIException):
    """训练任务不存在异常"""
    def __init__(self, message: Optional[str] = None, data: Any = None):
        super().__init__(
            error_code=ErrorCode.TRAINING_NOT_FOUND,
            message=message,
            data=data,
            status_code=404
        )


class ModelNotFoundException(APIException):
    """模型不存在异常"""
    def __init__(self, message: Optional[str] = None, data: Any = None):
        super().__init__(
            error_code=ErrorCode.MODEL_NOT_FOUND,
            message=message,
            data=data,
            status_code=404
        )


class DatabaseException(APIException):
    """数据库异常"""
    def __init__(self, message: Optional[str] = None, data: Any = None):
        super().__init__(
            error_code=ErrorCode.DATABASE_ERROR,
            message=message,
            data=data,
            status_code=500
        )


class InternalServerException(APIException):
    """服务器内部异常"""
    def __init__(self, message: Optional[str] = None, data: Any = None):
        super().__init__(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=message,
            data=data,
            status_code=500
        )