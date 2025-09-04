#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库迁移脚本：从SQLite迁移到PostgreSQL

此脚本执行以下操作：
1. 从SQLite数据库导出所有表的数据
2. 将数据导入到PostgreSQL数据库
3. 验证迁移是否成功

使用方法：
python migrate_sqlite_to_postgres.py --sqlite-url sqlite:///../data/database.db --postgres-url postgresql://postgres:postgres@localhost:5432/llm_trainer
"""

import argparse
import os
import sys
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, inspect, MetaData, Table, text
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

# 导入项目模型以确保所有表结构一致
from app import models


def backup_sqlite_data(sqlite_url, backup_dir):
    """从SQLite数据库备份所有表数据到JSON文件"""
    print(f"开始从SQLite备份数据到 {backup_dir}")
    
    # 创建备份目录
    os.makedirs(backup_dir, exist_ok=True)
    
    # 连接SQLite数据库
    sqlite_engine = create_engine(sqlite_url)
    inspector = inspect(sqlite_engine)
    
    # 获取所有表名
    table_names = inspector.get_table_names()
    print(f"发现表: {', '.join(table_names)}")
    
    # 为每个表创建备份
    for table_name in table_names:
        try:
            # 读取表数据
            df = pd.read_sql_table(table_name, sqlite_engine)
            
            # 保存为JSON文件
            backup_file = os.path.join(backup_dir, f"{table_name}.json")
            df.to_json(backup_file, orient='records')
            
            print(f"表 {table_name} 已备份，记录数: {len(df)}")
        except Exception as e:
            print(f"备份表 {table_name} 时出错: {str(e)}")
    
    print("SQLite数据备份完成")


def restore_to_postgres(postgres_url, backup_dir):
    """从备份文件恢复数据到PostgreSQL数据库"""
    print(f"开始将数据从 {backup_dir} 恢复到PostgreSQL")
    
    # 连接PostgreSQL数据库
    postgres_engine = create_engine(postgres_url)
    
    # 创建所有表结构
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(postgres_engine)
    
    # 清空所有表，避免主键冲突
    with postgres_engine.connect() as conn:
        conn.execute(text("TRUNCATE dataset, trainingjob, modelartifact RESTART IDENTITY CASCADE"))
        conn.commit()
    
    # 获取所有备份文件
    backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.json')]
    
    # 按表依赖顺序排序（确保先导入被引用的表）
    priority_tables = ['dataset.json', 'user.json', 'role.json']
    backup_files = sorted(backup_files, key=lambda x: 
                         (priority_tables.index(x) if x in priority_tables else 999))
    
    # 从备份文件恢复数据
    for backup_file in backup_files:
        table_name = backup_file.replace('.json', '')
        backup_path = os.path.join(backup_dir, backup_file)
        
        try:
            # 读取备份数据
            with open(backup_path, 'r') as f:
                data = json.load(f)
            
            if not data:
                print(f"表 {table_name} 没有数据，跳过")
                continue
                
            # 处理时间戳字段，将毫秒时间戳转换为datetime
            for record in data:
                # 为trainingjob表添加默认user_id
                if table_name == 'trainingjob' and 'user_id' not in record:
                    record['user_id'] = 1  # 设置默认用户ID
                
                for field in record:
                    # 检查字段名是否包含时间相关关键词
                    if any(time_field in field.lower() for time_field in ['created_at', 'updated_at', 'completed_at', 'started_at', 'last_login']):
                        if record[field] and isinstance(record[field], (int, float)):
                            # 将毫秒时间戳转换为datetime
                            from datetime import datetime
                            record[field] = datetime.fromtimestamp(record[field]/1000)
            
            # 将数据转换为DataFrame
            df = pd.DataFrame(data)
            
            # 对于trainingjob表，使用直接SQL插入
            if table_name == 'trainingjob':
                with postgres_engine.connect() as conn:
                    for _, row in df.iterrows():
                        # 构建插入语句
                        columns = ['id', 'dataset_id', 'user_id', 'status', 'model_name', 'epochs', 
                                  'learning_rate', 'batch_size', 'progress', 'log_file', 'started_at', 'completed_at']
                        values = [row.get(col, None) if col in row else None for col in columns]
                        
                        # 确保user_id有值
                        if values[2] is None:  # user_id是第三个字段
                            values[2] = 1
                            
                        # 构建SQL语句
                        placeholders = ', '.join([':'+col for col in columns])
                        columns_str = ', '.join(columns)
                        sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                        
                        # 创建参数字典
                        params = {col: values[i] for i, col in enumerate(columns)}
                        
                        # 执行SQL
                        conn.execute(text(sql), params)
                    
                    conn.commit()
                    print(f"表 {table_name} 已恢复，记录数: {len(df)}")
            else:
                # 其他表使用pandas to_sql
                df.to_sql(table_name, postgres_engine, if_exists='append', index=False)
                print(f"表 {table_name} 已恢复，记录数: {len(df)}")
        except Exception as e:
            print(f"恢复表 {table_name} 时出错: {str(e)}")
    
    print("数据已成功恢复到PostgreSQL")


def verify_migration(sqlite_url, postgres_url):
    """验证迁移是否成功，比较两个数据库中的记录数"""
    print("开始验证数据迁移")
    
    # 连接数据库
    sqlite_engine = create_engine(sqlite_url)
    postgres_engine = create_engine(postgres_url)
    
    # 获取SQLite中的所有表
    sqlite_inspector = inspect(sqlite_engine)
    sqlite_tables = sqlite_inspector.get_table_names()
    
    # 获取PostgreSQL中的所有表
    postgres_inspector = inspect(postgres_engine)
    postgres_tables = postgres_inspector.get_table_names()
    
    # 验证所有表都已迁移
    missing_tables = set(sqlite_tables) - set(postgres_tables)
    if missing_tables:
        print(f"警告：以下表在PostgreSQL中不存在: {', '.join(missing_tables)}")
    
    # 验证每个表的记录数
    for table in sqlite_tables:
        if table in postgres_tables:
            # 计算SQLite表中的记录数
            sqlite_count = pd.read_sql(f"SELECT COUNT(*) as count FROM {table}", sqlite_engine).iloc[0]['count']
            
            # 计算PostgreSQL表中的记录数
            postgres_count = pd.read_sql(f"SELECT COUNT(*) as count FROM {table}", postgres_engine).iloc[0]['count']
            
            if sqlite_count == postgres_count:
                print(f"表 {table}: 验证成功 ({sqlite_count} 条记录)")
            else:
                print(f"表 {table}: 验证失败! SQLite: {sqlite_count} 条记录, PostgreSQL: {postgres_count} 条记录")
        else:
            print(f"表 {table}: 在PostgreSQL中不存在，无法验证")
    
    print("数据迁移验证完成")


def main():
    parser = argparse.ArgumentParser(description='从SQLite迁移数据到PostgreSQL')
    parser.add_argument('--sqlite-url', required=True, help='SQLite数据库URL')
    parser.add_argument('--postgres-url', required=True, help='PostgreSQL数据库URL')
    parser.add_argument('--backup-dir', default='./data/backup', help='数据备份目录')
    parser.add_argument('--skip-backup', action='store_true', help='跳过备份步骤')
    parser.add_argument('--skip-restore', action='store_true', help='跳过恢复步骤')
    parser.add_argument('--skip-verify', action='store_true', help='跳过验证步骤')
    
    args = parser.parse_args()
    
    # 创建带时间戳的备份目录
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = os.path.join(args.backup_dir, f"migration_{timestamp}")
    
    try:
        # 备份SQLite数据
        if not args.skip_backup:
            backup_sqlite_data(args.sqlite_url, backup_dir)
        
        # 恢复数据到PostgreSQL
        if not args.skip_restore:
            restore_to_postgres(args.postgres_url, backup_dir)
        
        # 验证迁移
        if not args.skip_verify:
            verify_migration(args.sqlite_url, args.postgres_url)
        
        print("数据库迁移完成!")
    except Exception as e:
        print(f"迁移过程中出错: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()