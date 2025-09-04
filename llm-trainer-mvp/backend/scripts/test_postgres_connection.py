#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试PostgreSQL数据库连接和CRUD操作

此脚本执行以下操作：
1. 测试与PostgreSQL数据库的连接
2. 执行基本的CRUD操作测试
3. 测试事务和回滚功能

使用方法：
python test_postgres_connection.py
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 导入项目模块
from app.db import get_session, transaction, engine
from app.models import User
from app.core.config import settings
from sqlmodel import select, SQLModel


def test_connection():
    """测试数据库连接"""
    try:
        # 尝试连接数据库
        with engine.connect() as conn:
            result = conn.execute(select(1)).scalar()
            assert result == 1
            logger.info("数据库连接测试成功")
            return True
    except Exception as e:
        logger.error(f"数据库连接测试失败: {str(e)}")
        return False


def test_crud_operations():
    """测试基本的CRUD操作"""
    try:
        # 创建测试用户
        test_user = User(
            username="test_postgres_user",
            email="test_postgres@example.com",
            full_name="Test PostgreSQL User",
            hashed_password="$2b$12$test_hash_for_testing_only",
            is_active=True,
            is_superuser=False
        )
        
        # 创建操作
        with get_session() as session:
            session.add(test_user)
            session.commit()
            session.refresh(test_user)
            user_id = test_user.id
            logger.info(f"创建用户成功，ID: {user_id}")
        
        # 读取操作
        with get_session() as session:
            user = session.get(User, user_id)
            assert user is not None
            assert user.username == "test_postgres_user"
            logger.info(f"读取用户成功: {user.username}")
        
        # 更新操作
        with get_session() as session:
            user = session.get(User, user_id)
            user.full_name = "Updated PostgreSQL Test User"
            session.add(user)
            session.commit()
            session.refresh(user)
            assert user.full_name == "Updated PostgreSQL Test User"
            logger.info(f"更新用户成功: {user.full_name}")
        
        # 删除操作
        with get_session() as session:
            user = session.get(User, user_id)
            session.delete(user)
            session.commit()
            logger.info(f"删除用户成功")
        
        # 验证删除
        with get_session() as session:
            user = session.get(User, user_id)
            assert user is None
            logger.info(f"验证删除成功")
        
        return True
    except Exception as e:
        logger.error(f"CRUD操作测试失败: {str(e)}")
        return False


def test_transaction():
    """测试事务和回滚功能"""
    try:
        # 创建测试用户
        test_user = User(
            username="transaction_test_user",
            email="transaction_test@example.com",
            full_name="Transaction Test User",
            hashed_password="$2b$12$test_hash_for_testing_only",
            is_active=True,
            is_superuser=False
        )
        
        # 测试成功的事务
        with transaction() as session:
            session.add(test_user)
            # 事务会自动提交
        
        # 验证用户已创建
        with get_session() as session:
            user = session.exec(select(User).where(User.username == "transaction_test_user")).first()
            assert user is not None
            user_id = user.id
            logger.info(f"事务提交测试成功，用户ID: {user_id}")
        
        # 测试回滚的事务
        try:
            with transaction() as session:
                # 更新用户
                user = session.get(User, user_id)
                user.full_name = "This update should be rolled back"
                session.add(user)
                
                # 故意引发异常
                raise ValueError("测试事务回滚")
                # 事务应该回滚
        except ValueError:
            pass  # 预期的异常
        
        # 验证更新已回滚
        with get_session() as session:
            user = session.get(User, user_id)
            assert user.full_name == "Transaction Test User"
            logger.info(f"事务回滚测试成功")
        
        # 清理测试数据
        with get_session() as session:
            user = session.get(User, user_id)
            session.delete(user)
            session.commit()
        
        return True
    except Exception as e:
        logger.error(f"事务测试失败: {str(e)}")
        return False


def main():
    logger.info(f"开始测试PostgreSQL数据库连接和操作")
    logger.info(f"数据库URL: {settings.DATABASE_URL}")
    
    # 测试连接
    if not test_connection():
        logger.error("数据库连接测试失败，终止后续测试")
        return False
    
    # 测试CRUD操作
    if not test_crud_operations():
        logger.error("CRUD操作测试失败")
        return False
    
    # 测试事务
    if not test_transaction():
        logger.error("事务测试失败")
        return False
    
    logger.info("所有测试通过!")
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)