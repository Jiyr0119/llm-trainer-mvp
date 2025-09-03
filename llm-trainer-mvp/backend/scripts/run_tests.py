#!/usr/bin/env python
"""
测试运行脚本
用于执行后端测试并生成覆盖率报告
"""

import os
import sys
import subprocess

def run_tests():
    """运行测试并生成覆盖率报告"""
    # 设置测试环境变量
    os.environ["APP_ENV"] = "test"
    
    # 构建pytest命令
    cmd = [
        "pytest",
        "-v",  # 详细输出
        "--cov=app",  # 覆盖率测量范围
        "--cov-report=term",  # 终端输出覆盖率
        "--cov-report=html:coverage_html",  # HTML覆盖率报告
    ]
    
    # 运行测试
    result = subprocess.run(cmd)
    
    # 返回测试结果
    return result.returncode

def main():
    """主函数"""
    print("开始运行测试...", flush=True)
    exit_code = run_tests()
    
    if exit_code == 0:
        print("\n✅ 测试通过！")
        print("覆盖率报告已生成在 coverage_html 目录中")
    else:
        print("\n❌ 测试失败！")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())