import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# 请求ID上下文，用于在整个请求生命周期中跟踪请求ID
class RequestIdContext:
    _request_id = None

    @classmethod
    def get_request_id(cls) -> str:
        """获取当前请求ID，如果不存在则生成一个新的"""
        if cls._request_id is None:
            cls._request_id = str(uuid.uuid4())
        return cls._request_id

    @classmethod
    def set_request_id(cls, request_id: str) -> None:
        """设置请求ID"""
        cls._request_id = request_id

    @classmethod
    def clear_request_id(cls) -> None:
        """清除请求ID"""
        cls._request_id = None


# JSON格式日志格式化器
class JsonFormatter(logging.Formatter):
    """自定义日志格式化器，将日志输出为JSON格式"""

    def __init__(self, *args, **kwargs):
        self.include_timestamp = kwargs.pop('include_timestamp', True)
        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord) -> str:
        """将日志记录格式化为JSON字符串"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() if self.include_timestamp else None,
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
            'path': record.pathname,
            'line': record.lineno,
            'request_id': RequestIdContext.get_request_id(),
        }

        # 添加异常信息（如果有）
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # 添加额外的上下文信息（如果有）
        if hasattr(record, 'extra') and record.extra:
            log_data.update(record.extra)

        # 移除None值
        log_data = {k: v for k, v in log_data.items() if v is not None}

        return json.dumps(log_data, ensure_ascii=False)


# 日志配置函数
def setup_logger(name: str, log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """配置并返回一个日志记录器

    Args:
        name: 日志记录器名称
        log_file: 日志文件路径，如果为None则只输出到控制台
        level: 日志级别

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 清除现有的处理器
    if logger.handlers:
        logger.handlers.clear()

    # 创建JSON格式化器
    json_formatter = JsonFormatter()

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)

    # 文件处理器（如果指定了日志文件）
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)

    return logger


# 创建一个用于记录请求信息的日志记录器
request_logger = setup_logger('request')


def log_request_info(request_method: str, request_path: str, status_code: int, 
                    process_time: float, extra: Dict[str, Any] = None) -> None:
    """记录HTTP请求信息

    Args:
        request_method: HTTP方法（GET, POST等）
        request_path: 请求路径
        status_code: HTTP状态码
        process_time: 请求处理时间（毫秒）
        extra: 额外的日志信息
    """
    log_data = {
        'method': request_method,
        'path': request_path,
        'status_code': status_code,
        'process_time_ms': round(process_time * 1000, 2),
        'extra': extra or {}
    }

    # 根据状态码确定日志级别
    if status_code >= 500:
        request_logger.error(f"Request completed", extra={'extra': log_data})
    elif status_code >= 400:
        request_logger.warning(f"Request completed", extra={'extra': log_data})
    else:
        request_logger.info(f"Request completed", extra={'extra': log_data})