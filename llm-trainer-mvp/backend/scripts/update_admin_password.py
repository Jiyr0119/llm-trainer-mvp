#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
更新管理员密码脚本
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_db_context
from app.models import User, get_password_hash
from sqlmodel import select

def update_admin_password():
    with get_db_context() as db:
        # 查找admin用户
        statement = select(User).where(User.username == 'admin')
        admin = db.exec(statement).first()
        
        if admin:
            # 更新密码为admin123
            admin.hashed_password = get_password_hash("admin123")
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"Updated admin password. New hash: {admin.hashed_password}")
        else:
            print("Admin user not found")

if __name__ == "__main__":
    update_admin_password()