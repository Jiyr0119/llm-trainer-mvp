#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库备份脚本：备份PostgreSQL数据库

此脚本执行以下操作：
1. 使用pg_dump创建PostgreSQL数据库的备份
2. 将备份文件保存到指定目录
3. 管理备份文件的保留策略（保留最近N个备份）

使用方法：
python backup_postgres.py --db-name llm_trainer --backup-dir ../data/backups --keep 5
"""

import argparse
import os
import sys
import subprocess
from datetime import datetime
import logging
import glob

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def create_backup(db_name, backup_dir, host='localhost', port=5432, username='postgres', password=None):
    """创建PostgreSQL数据库备份"""
    # 确保备份目录存在
    os.makedirs(backup_dir, exist_ok=True)
    
    # 创建带时间戳的备份文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f"{db_name}_{timestamp}.sql")
    
    # 构建pg_dump命令
    cmd = [
        'pg_dump',
        f'--dbname={db_name}',
        f'--host={host}',
        f'--port={port}',
        f'--username={username}',
        '--format=plain',
        f'--file={backup_file}',
    ]
    
    # 设置环境变量
    env = os.environ.copy()
    if password:
        env['PGPASSWORD'] = password
    
    try:
        # 执行备份命令
        logger.info(f"开始备份数据库 {db_name} 到 {backup_file}")
        process = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        logger.info(f"数据库备份成功: {backup_file}")
        return backup_file
    except subprocess.CalledProcessError as e:
        logger.error(f"备份失败: {e.stderr}")
        raise


def restore_backup(backup_file, db_name, host='localhost', port=5432, username='postgres', password=None):
    """从备份文件恢复PostgreSQL数据库"""
    if not os.path.exists(backup_file):
        logger.error(f"备份文件不存在: {backup_file}")
        return False
    
    # 构建psql命令
    cmd = [
        'psql',
        f'--dbname={db_name}',
        f'--host={host}',
        f'--port={port}',
        f'--username={username}',
        f'--file={backup_file}',
    ]
    
    # 设置环境变量
    env = os.environ.copy()
    if password:
        env['PGPASSWORD'] = password
    
    try:
        # 执行恢复命令
        logger.info(f"开始从 {backup_file} 恢复数据库 {db_name}")
        process = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        logger.info(f"数据库恢复成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"恢复失败: {e.stderr}")
        return False


def manage_backups(backup_dir, keep=5):
    """管理备份文件，只保留最近的N个备份"""
    if not os.path.exists(backup_dir):
        logger.warning(f"备份目录不存在: {backup_dir}")
        return
    
    # 获取所有备份文件
    backup_files = glob.glob(os.path.join(backup_dir, "*.sql"))
    
    # 按修改时间排序
    backup_files.sort(key=os.path.getmtime)
    
    # 如果备份文件数量超过保留数量，删除旧的备份
    if len(backup_files) > keep:
        files_to_delete = backup_files[:-keep]
        for file in files_to_delete:
            try:
                os.remove(file)
                logger.info(f"删除旧备份: {file}")
            except Exception as e:
                logger.error(f"删除备份文件失败: {file}, 错误: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='备份PostgreSQL数据库')
    parser.add_argument('--db-name', required=True, help='数据库名称')
    parser.add_argument('--backup-dir', default='../data/backups', help='备份目录')
    parser.add_argument('--host', default='localhost', help='数据库主机')
    parser.add_argument('--port', type=int, default=5432, help='数据库端口')
    parser.add_argument('--username', default='postgres', help='数据库用户名')
    parser.add_argument('--password', help='数据库密码')
    parser.add_argument('--keep', type=int, default=5, help='保留的备份数量')
    parser.add_argument('--restore', help='要恢复的备份文件路径')
    
    args = parser.parse_args()
    
    try:
        if args.restore:
            # 恢复模式
            success = restore_backup(
                args.restore, args.db_name, args.host, args.port, args.username, args.password
            )
            sys.exit(0 if success else 1)
        else:
            # 备份模式
            backup_file = create_backup(
                args.db_name, args.backup_dir, args.host, args.port, args.username, args.password
            )
            manage_backups(args.backup_dir, args.keep)
            sys.exit(0)
    except Exception as e:
        logger.error(f"操作失败: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()