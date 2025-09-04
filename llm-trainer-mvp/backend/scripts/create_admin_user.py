#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建管理员用户脚本
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_session
from app.models import User
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
        with get_session() as session:
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
                hashed_password='$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  # 密码: password
                full_name='Admin User',
                role='admin',
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