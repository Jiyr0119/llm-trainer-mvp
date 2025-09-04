# 后端配置和设置
import os
from typing import Dict, Any, Optional, List
from pydantic_settings import BaseSettings  # 导入Pydantic的设置基类，用于环境变量和配置管理
from pydantic import Field
from functools import lru_cache  # 导入LRU缓存装饰器，用于缓存配置实例
import logging

# 定义可用环境
class Environment:
    DEV = "dev"
    TEST = "test"
    PROD = "prod"

# 应用设置类，继承自BaseSettings
class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "LLM Trainer"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "LLM训练与推理服务"
    
    # 环境配置
    APP_ENV: str = Field(default=Environment.DEV, env="APP_ENV")
    ENV: str = Field(default=Environment.DEV, env="APP_ENV")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # 服务器配置
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8001, env="PORT")
    
    # 数据库配置
    DATABASE_URL: str = Field(default="sqlite:///../data/database.db", env="DATABASE_URL")
    # 数据库连接池配置
    DB_POOL_SIZE: int = Field(default=5, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=10, env="DB_MAX_OVERFLOW")
    DB_POOL_TIMEOUT: int = Field(default=30, env="DB_POOL_TIMEOUT")
    DB_POOL_RECYCLE: int = Field(default=1800, env="DB_POOL_RECYCLE")
    
    # 文件存储配置
    UPLOAD_PATH: str = Field(default="../data/uploads", env="UPLOAD_PATH")
    MODEL_PATH: str = Field(default="../data/models", env="MODEL_PATH")
    LOG_PATH: str = Field(default="../data/logs", env="LOG_PATH")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="../data/training.log", env="LOG_FILE")
    
    # CORS配置
    CORS_ORIGINS: str = Field(default="*", env="CORS_ORIGINS")
    
    # 模型配置
    DEFAULT_MODEL: str = Field(default="bert-base-uncased", env="DEFAULT_MODEL")
    
    # 训练配置
    DEFAULT_BATCH_SIZE: int = Field(default=8, env="DEFAULT_BATCH_SIZE")
    DEFAULT_EPOCHS: int = Field(default=3, env="DEFAULT_EPOCHS")
    DEFAULT_LEARNING_RATE: float = Field(default=2e-5, env="DEFAULT_LEARNING_RATE")
    
    # 安全配置
    SECRET_KEY: str = Field(default="your-secret-key-for-jwt-please-change-in-production", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    PASSWORD_BCRYPT_ROUNDS: int = Field(default=12, env="PASSWORD_BCRYPT_ROUNDS")
    
    # 内部配置类，用于设置BaseSettings的行为
    class Config:
        env_file = ".env"  # 指定环境变量文件，从中读取配置
        env_file_encoding = "utf-8"
        case_sensitive = False  # 环境变量名称不区分大小写

# 开发环境配置
class DevSettings(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    class Config:
        env_file = ".env.dev"

# 测试环境配置
class TestSettings(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env.test"

# 生产环境配置
class ProdSettings(Settings):
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    CORS_ORIGINS: List[str] = ["https://llm-trainer.example.com"]
    
    class Config:
        env_file = ".env.prod"

# 获取设置的函数，使用lru_cache装饰器缓存结果
# 这样可以避免重复创建Settings实例，提高性能
@lru_cache()
def get_settings() -> Settings:
    env = os.getenv("APP_ENV", Environment.DEV)
    
    if env == Environment.PROD:
        return ProdSettings()
    elif env == Environment.TEST:
        return TestSettings()
    else:
        return DevSettings()

# 创建全局设置实例
settings = get_settings()

# 配置日志级别映射
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# 获取日志级别
def get_log_level() -> int:
    return LOG_LEVEL_MAP.get(settings.LOG_LEVEL, logging.INFO)