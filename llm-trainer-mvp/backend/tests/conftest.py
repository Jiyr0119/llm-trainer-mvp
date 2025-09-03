import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# 导入应用和数据库模型
from app.core.config import get_settings
from main import app

# 设置测试环境变量
os.environ["APP_ENV"] = "test"

@pytest.fixture(scope="session")
def test_settings():
    """返回测试环境配置"""
    return get_settings()

@pytest.fixture(scope="function")
def test_db_engine():
    """创建测试数据库引擎"""
    # 使用内存数据库进行测试
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # 创建所有表
    SQLModel.metadata.create_all(engine)
    
    yield engine
    
    # 测试后清理
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """创建测试数据库会话"""
    with Session(test_db_engine) as session:
        yield session

@pytest.fixture(scope="function")
def client(test_db_session):
    """创建测试客户端"""
    # 依赖覆盖
    def get_test_db():
        yield test_db_session
    
    # 替换应用中的数据库依赖
    app.dependency_overrides = {}
    
    # 创建测试客户端
    with TestClient(app) as test_client:
        yield test_client
    
    # 测试后清理依赖覆盖
    app.dependency_overrides = {}