# 自定义异常类
# 提供业务逻辑相关的异常定义

from typing import Any, Optional


class BusinessException(Exception):
    """业务异常基类"""
    
    def __init__(
        self,
        message: str,
        code: str = "BUSINESS_ERROR",
        data: Any = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data


class ValidationException(BusinessException):
    """数据验证异常"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field


class ResourceNotFoundException(BusinessException):
    """资源不存在异常"""
    
    def __init__(self, resource: str, resource_id: Any):
        message = f"{resource} (ID: {resource_id}) 不存在"
        super().__init__(message, code="RESOURCE_NOT_FOUND")
        self.resource = resource
        self.resource_id = resource_id


class DatasetException(BusinessException):
    """数据集相关异常"""
    
    def __init__(self, message: str, dataset_id: Optional[int] = None):
        super().__init__(message, code="DATASET_ERROR")
        self.dataset_id = dataset_id


class TrainingException(BusinessException):
    """训练相关异常"""
    
    def __init__(self, message: str, job_id: Optional[int] = None):
        super().__init__(message, code="TRAINING_ERROR")
        self.job_id = job_id


class PredictionException(BusinessException):
    """预测相关异常"""
    
    def __init__(self, message: str, model_id: Optional[int] = None):
        super().__init__(message, code="PREDICTION_ERROR")
        self.model_id = model_id


class FileException(BusinessException):
    """文件操作异常"""
    
    def __init__(self, message: str, file_path: Optional[str] = None):
        super().__init__(message, code="FILE_ERROR")
        self.file_path = file_path