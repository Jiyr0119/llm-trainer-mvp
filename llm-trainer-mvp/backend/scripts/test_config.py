#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置测试脚本
用于测试不同环境的配置加载
"""

import os
import sys
import subprocess
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent
SCRIPT_DIR = Path(__file__).parent

# 支持的环境类型
ENV_TYPES = ['dev', 'test', 'prod']

def print_header(text):
    """打印带有分隔符的标题"""
    print("\n" + "=" * 50)
    print(f" {text} ")
    print("=" * 50)

def test_env(env_type):
    """测试指定环境的配置"""
    print_header(f"测试 {env_type} 环境配置")
    
    # 切换环境
    load_env_script = SCRIPT_DIR / "load_env.py"
    subprocess.run([sys.executable, str(load_env_script), env_type], check=True)
    
    # 创建测试脚本
    test_script = """
#!/usr/bin/env python
from app.core.config import settings, get_log_level
import json

# 收集配置信息
config_info = {
    "APP_ENV": str(settings.APP_ENV),
    "DEBUG": settings.DEBUG,
    "HOST": settings.HOST,
    "PORT": settings.PORT,
    "DATABASE_URL": settings.DATABASE_URL,
    "UPLOAD_PATH": settings.UPLOAD_PATH,
    "MODEL_PATH": settings.MODEL_PATH,
    "LOG_PATH": settings.LOG_PATH,
    "LOG_LEVEL": settings.LOG_LEVEL,
    "CORS_ORIGINS": settings.CORS_ORIGINS,
    "DEFAULT_MODEL": settings.DEFAULT_MODEL,
    "DEFAULT_BATCH_SIZE": settings.DEFAULT_BATCH_SIZE,
    "DEFAULT_EPOCHS": settings.DEFAULT_EPOCHS,
    "DEFAULT_LEARNING_RATE": settings.DEFAULT_LEARNING_RATE,
}

# 打印配置信息
print(json.dumps(config_info, indent=2, ensure_ascii=False))
    """
    
    temp_script_path = ROOT_DIR / "temp_config_test.py"
    with open(temp_script_path, "w") as f:
        f.write(test_script)
    
    try:
        # 运行测试脚本
        result = subprocess.run(
            [sys.executable, str(temp_script_path)],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"错误: {e}")
        print(e.stdout)
        print(e.stderr)
    finally:
        # 清理临时脚本
        temp_script_path.unlink()

def main():
    print_header("配置测试开始")
    
    for env in ENV_TYPES:
        test_env(env)
    
    print_header("配置测试完成")

if __name__ == "__main__":
    main()