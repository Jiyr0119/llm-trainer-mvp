#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
环境变量加载脚本
用于在不同环境之间切换配置
"""

import os
import sys
import argparse
import shutil
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent

# 支持的环境类型
ENV_TYPES = ['dev', 'test', 'prod']

def load_env(env_type):
    """加载指定环境的配置文件"""
    if env_type not in ENV_TYPES:
        print(f"错误: 不支持的环境类型 '{env_type}'。支持的环境类型: {', '.join(ENV_TYPES)}")
        sys.exit(1)
        
    source_file = ROOT_DIR / f".env.{env_type}"
    target_file = ROOT_DIR / ".env"
    
    if not source_file.exists():
        print(f"错误: 环境配置文件 '{source_file}' 不存在")
        sys.exit(1)
    
    try:
        shutil.copy2(source_file, target_file)
        print(f"成功: 已加载 {env_type} 环境配置")
    except Exception as e:
        print(f"错误: 无法加载环境配置: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="加载指定环境的配置文件")
    parser.add_argument(
        "env", 
        choices=ENV_TYPES,
        help=f"要加载的环境类型: {', '.join(ENV_TYPES)}"
    )
    
    args = parser.parse_args()
    load_env(args.env)

if __name__ == "__main__":
    main()