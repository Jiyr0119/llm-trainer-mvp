#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
初始化PostgreSQL数据库表结构

此脚本执行以下操作：
1. 连接到PostgreSQL数据库
2. 创建所有定义的表结构

使用方法：
python init_postgres_db.py
"""

import os
import sys
import logging
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
from app.db import init_db, engine
from app.core.config import settings


def main():
    logger.info(f"开始初始化PostgreSQL数据库表结构")
    logger.info(f"数据库URL: {settings.DATABASE_URL}")
    
    try:
        # 初始化数据库表结构
        init_db()
        logger.info("数据库表结构初始化成功")
        return True
    except Exception as e:
        logger.error(f"数据库表结构初始化失败: {str(e)}")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)