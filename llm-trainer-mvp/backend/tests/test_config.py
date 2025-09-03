import os
import pytest
from app.core.config import get_settings, Settings

def test_default_config():
    """测试默认配置加载"""
    # 保存原始环境变量
    original_env = os.environ.get("APP_ENV")
    
    try:
        # 设置为开发环境
        os.environ["APP_ENV"] = "dev"
        settings = get_settings()
        
        # 验证开发环境配置
        assert settings.APP_ENV == "dev"
        assert settings.DEBUG == True
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8001
        
        # 设置为测试环境
        os.environ["APP_ENV"] = "test"
        settings = get_settings(force_reload=True)
        
        # 验证测试环境配置
        assert settings.APP_ENV == "test"
        assert settings.DEBUG == True
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8001
        
        # 设置为生产环境
        os.environ["APP_ENV"] = "prod"
        settings = get_settings(force_reload=True)
        
        # 验证生产环境配置
        assert settings.APP_ENV == "prod"
        assert settings.DEBUG == False
        
    finally:
        # 恢复原始环境变量
        if original_env:
            os.environ["APP_ENV"] = original_env
        else:
            del os.environ["APP_ENV"]

def test_override_config():
    """测试环境变量覆盖配置"""
    # 保存原始环境变量
    original_env = {}
    for key in ["APP_ENV", "DEBUG", "HOST", "PORT"]:
        if key in os.environ:
            original_env[key] = os.environ[key]
    
    try:
        # 设置环境变量
        os.environ["APP_ENV"] = "test"
        os.environ["DEBUG"] = "false"  # 覆盖测试环境的默认值
        os.environ["HOST"] = "127.0.0.1"  # 覆盖默认值
        os.environ["PORT"] = "9000"  # 覆盖默认值
        
        # 重新加载配置
        settings = get_settings(force_reload=True)
        
        # 验证配置被环境变量覆盖
        assert settings.APP_ENV == "test"
        assert settings.DEBUG == False  # 被环境变量覆盖
        assert settings.HOST == "127.0.0.1"  # 被环境变量覆盖
        assert settings.PORT == 9000  # 被环境变量覆盖
        
    finally:
        # 恢复原始环境变量
        for key in ["APP_ENV", "DEBUG", "HOST", "PORT"]:
            if key in original_env:
                os.environ[key] = original_env[key]
            elif key in os.environ:
                del os.environ[key]