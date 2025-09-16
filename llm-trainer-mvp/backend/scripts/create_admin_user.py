#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建管理员用户脚本
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

# 加载.env.dev文件中的环境变量
env_file = os.path.join(project_root, '.env.dev')
load_dotenv(env_file)
print(f"加载环境变量文件: {env_file}")
print(f"数据库URL环境变量: {os.environ.get('DATABASE_URL', '未设置')}")

from app.db import get_db_context
from app.models import User, get_password_hash
from sqlmodel import Session, select
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_admin_user():
    """创建管理员用户"""
    try:
        with get_db_context() as session:
            # 检查用户是否已存在
            statement = select(User).where(User.id == 1)
            existing_user = session.exec(statement).first()
            
            if existing_user:
                logger.info(f"ID为1的用户已存在: {existing_user.username}")
                return
            
            # 创建管理员用户
            user = User(
                id=1,
                username='admin',
                email='admin@example.com',
                hashed_password=get_password_hash("admin123"),  # 密码: admin123
                full_name='Admin User',
                role='ADMIN',  # 使用正确的枚举值
                is_active=True
            )
            
            session.add(user)
            session.commit()
            logger.info("管理员用户创建成功")
    except Exception as e:
        logger.error(f"创建管理员用户时出错: {e}")
        raise

if __name__ == "__main__":
    create_admin_user()