import requests
import json
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API基础URL
BASE_URL = "http://localhost:8000"

def test_api_error_handling():
    """测试API错误处理"""
    logger.info("开始测试API错误处理")
    
    # 测试1: 请求不存在的资源 (404)
    try:
        response = requests.get(f"{BASE_URL}/non_existent_endpoint")
        logger.info(f"测试1 - 状态码: {response.status_code}")
        logger.info(f"测试1 - 响应: {response.text}")
        assert response.status_code == 404, "应该返回404状态码"
        assert "not found" in response.text.lower(), "响应应该包含'not found'信息"
    except Exception as e:
        logger.error(f"测试1失败: {str(e)}")
    
    # 测试2: 请求参数验证错误 (422)
    try:
        # 发送缺少必要参数的请求
        response = requests.post(f"{BASE_URL}/train", json={})
        logger.info(f"测试2 - 状态码: {response.status_code}")
        logger.info(f"测试2 - 响应: {response.text}")
        assert response.status_code == 422, "应该返回422状态码"
        response_data = response.json()
        assert not response_data.get("success", True), "success字段应该为false"
        assert "code" in response_data, "响应应该包含code字段"
    except Exception as e:
        logger.error(f"测试2失败: {str(e)}")
    
    # 测试3: 请求不存在的数据集 (404 - 自定义异常)
    try:
        response = requests.get(f"{BASE_URL}/dataset/preview/999999")
        logger.info(f"测试3 - 状态码: {response.status_code}")
        logger.info(f"测试3 - 响应: {response.text}")
        assert response.status_code == 404, "应该返回404状态码"
        response_data = response.json()
        assert not response_data.get("success", True), "success字段应该为false"
        assert "code" in response_data, "响应应该包含code字段"
        assert "DATASET_NOT_FOUND" in response_data.get("code", ""), "错误码应该包含DATASET_NOT_FOUND"
    except Exception as e:
        logger.error(f"测试3失败: {str(e)}")
    
    logger.info("API错误处理测试完成")

def check_log_structure():
    """检查日志结构"""
    logger.info("开始检查日志结构")
    
    # 检查日志文件是否存在
    log_file = "../data/training.log"
    if not os.path.exists(log_file):
        logger.error(f"日志文件不存在: {log_file}")
        return
    
    # 读取最新的几行日志
    with open(log_file, 'r') as f:
        # 读取最后10行
        lines = f.readlines()
        last_lines = lines[-10:] if len(lines) >= 10 else lines
    
    # 检查日志格式是否为JSON
    for line in last_lines:
        try:
            log_entry = json.loads(line.strip())
            # 检查关键字段
            assert "timestamp" in log_entry, "日志应该包含timestamp字段"
            assert "level" in log_entry, "日志应该包含level字段"
            assert "message" in log_entry, "日志应该包含message字段"
            
            # 检查请求ID字段
            if "request_id" in log_entry:
                logger.info(f"找到请求ID: {log_entry['request_id']}")
            
            logger.info(f"日志结构正确: {line[:100]}...")
        except json.JSONDecodeError:
            logger.error(f"日志不是有效的JSON格式: {line}")
        except AssertionError as e:
            logger.error(f"日志缺少必要字段: {str(e)}, 日志: {line}")
    
    logger.info("日志结构检查完成")

if __name__ == "__main__":
    logger.info("开始测试异常处理和日志记录")
    
    # 确保后端服务正在运行
    try:
        requests.get(f"{BASE_URL}/health")
        logger.info("后端服务正在运行")
    except requests.exceptions.ConnectionError:
        logger.error(f"无法连接到后端服务: {BASE_URL}")
        logger.info("请确保后端服务已启动")
        exit(1)
    
    # 运行测试
    test_api_error_handling()
    check_log_structure()
    
    logger.info("测试完成")