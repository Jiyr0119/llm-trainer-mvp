# 后端配置和设置
from pydantic_settings import BaseSettings  # 导入Pydantic的设置基类，用于环境变量和配置管理
from functools import lru_cache  # 导入LRU缓存装饰器，用于缓存配置实例


# 应用设置类，继承自BaseSettings
class Settings(BaseSettings):
    # 数据库URL，默认使用项目data目录下的SQLite文件
    # 格式：sqlite:///文件路径
    DATABASE_URL: str = "sqlite:///../data/database.db"

    # 内部配置类，用于设置BaseSettings的行为
    class Config:
        env_file = ".env"  # 指定环境变量文件，从中读取配置
        case_sensitive = False  # 环境变量名称不区分大小写


# 获取设置的函数，使用lru_cache装饰器缓存结果
# 这样可以避免重复创建Settings实例，提高性能
@lru_cache()
def get_settings() -> "Settings":
    return Settings()


# 创建全局设置实例
settings = get_settings()