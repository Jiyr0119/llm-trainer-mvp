# API标准化测试
# 测试所有API接口是否遵循标准响应格式

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import app
from app.core.response import APIResponse
from app.core.errors import ErrorCode, APIException
from app.services.dataset_service import dataset_service
from app.services.training_service import TrainingService
from app.services.prediction_service import PredictionService


# 创建测试客户端
client = TestClient(app)

class TestAPIStandardization:
    """API标准化测试类"""
    
    def test_health_endpoint_format(self):
        """测试健康检查端点响应格式"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        # 验证标准响应格式
        assert "success" in data
        assert "code" in data
        assert "message" in data
        assert "data" in data
        
        assert data["success"] is True
        assert data["code"] == 200
        assert isinstance(data["message"], str)
        assert isinstance(data["data"], dict)
    
    def test_root_endpoint_format(self):
        """测试根路径端点响应格式"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        # 验证标准响应格式
        assert "success" in data
        assert "code" in data
        assert "message" in data
        assert "data" in data
        
        assert data["success"] is True
        assert data["code"] == 200
    
    @patch.object(dataset_service, 'get_all_datasets')
    def test_datasets_list_format(self, mock_get_datasets):
        """测试数据集列表端点响应格式"""
        # Mock数据
        mock_get_datasets.return_value = [
            {"id": 1, "name": "test1", "filename": "test1.csv"},
            {"id": 2, "name": "test2", "filename": "test2.csv"}
        ]
        
        response = client.get("/api/datasets")
        assert response.status_code == 200
        
        data = response.json()
        # 验证标准响应格式
        assert "success" in data
        assert "code" in data
        assert "message" in data
        assert "data" in data
        
        assert data["success"] is True
        assert data["code"] == 200
        assert isinstance(data["data"], list)
    
    @patch.object(dataset_service, 'preview_dataset')
    def test_dataset_preview_format(self, mock_preview):
        """测试数据集预览端点响应格式"""
        # Mock数据
        mock_preview.return_value = {
            "preview": [{"text": "test", "label": "positive"}],
            "total_rows": 100
        }
        
        response = client.get("/api/datasets/1/preview")
        assert response.status_code == 200
        
        data = response.json()
        # 验证标准响应格式
        assert "success" in data
        assert "code" in data
        assert "message" in data
        assert "data" in data
        
        assert data["success"] is True
        assert data["code"] == 200
    
    def test_validation_error_format(self):
        """测试参数验证错误响应格式"""
        # 发送无效参数请求
        response = client.get("/api/datasets/invalid_id/preview")
        assert response.status_code == 422
        
        data = response.json()
        # 验证标准错误响应格式
        assert "success" in data
        assert "code" in data
        assert "message" in data
        
        assert data["success"] is False
        assert data["code"] == ErrorCode.INVALID_PARAMS.code
        assert isinstance(data["message"], str)
    
    def test_not_found_error_format(self):
        """测试404错误响应格式"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        
        data = response.json()
        # 验证标准错误响应格式
        assert "success" in data
        assert "code" in data
        assert "message" in data
        
        assert data["success"] is False


class TestAPIExceptionHandling:
    """API异常处理测试类"""
    
    @patch.object(dataset_service, 'get_all_datasets')
    def test_api_exception_handling(self, mock_get_datasets):
        """测试API异常处理"""
        # Mock抛出API异常
        from app.core.errors import DatasetNotFoundException
        mock_get_datasets.side_effect = DatasetNotFoundException("测试异常")
        
        response = client.get("/api/datasets")
        assert response.status_code == 404
        
        data = response.json()
        # 验证异常响应格式
        assert data["success"] is False
        assert data["code"] == ErrorCode.DATASET_NOT_FOUND.code
        assert "测试异常" in data["message"]
    
    @patch.object(dataset_service, 'get_all_datasets')
    def test_general_exception_handling(self, mock_get_datasets):
        """测试通用异常处理"""
        # Mock抛出通用异常
        mock_get_datasets.side_effect = Exception("数据库连接失败")
        
        response = client.get("/api/datasets")
        assert response.status_code == 500
        
        data = response.json()
        # 验证异常响应格式
        assert data["success"] is False
        assert data["code"] == ErrorCode.INTERNAL_SERVER_ERROR.code
        assert isinstance(data["message"], str)


class TestResponseConsistency:
    """响应一致性测试类"""
    
    def get_all_api_endpoints(self):
        """获取所有API端点"""
        return [
            ("/health", "GET"),
            ("/", "GET"),
            ("/api/datasets", "GET"),
            ("/api/train/jobs", "GET"),
            ("/api/train/status/1", "GET"),
        ]
    
    def test_response_format_consistency(self):
        """测试所有端点响应格式一致性"""
        endpoints = self.get_all_api_endpoints()
        
        for endpoint, method in endpoints:
            try:
                if method == "GET":
                    response = client.get(endpoint)
                else:
                    continue  # 暂时只测试GET端点
                
                # 检查响应是否包含标准字段
                if response.status_code < 400:  # 成功响应
                    data = response.json()
                    assert "success" in data, f"端点 {endpoint} 缺少 'success' 字段"
                    assert "code" in data, f"端点 {endpoint} 缺少 'code' 字段"
                    assert "message" in data, f"端点 {endpoint} 缺少 'message' 字段"
                    
                    # 成功响应应该有success=True
                    assert data["success"] is True, f"端点 {endpoint} success字段应为True"
                    
            except Exception as e:
                pytest.fail(f"端点 {endpoint} 测试失败: {str(e)}")


class TestErrorCodeMapping:
    """错误码映射测试类"""
    
    def test_error_code_values(self):
        """测试错误码值是否正确"""
        # 测试所有错误码是否符合规范
        assert ErrorCode.UNKNOWN_ERROR.code == 10000
        assert ErrorCode.INVALID_PARAMS.code == 10001
        assert ErrorCode.RESOURCE_NOT_FOUND.code == 10002
        
        assert ErrorCode.DATASET_NOT_FOUND.code == 20001
        assert ErrorCode.DATASET_FORMAT_ERROR.code == 20002
        
        assert ErrorCode.TRAINING_FAILED.code == 30001
        assert ErrorCode.TRAINING_NOT_FOUND.code == 30002
        
        assert ErrorCode.MODEL_NOT_FOUND.code == 40001
        assert ErrorCode.PREDICTION_FAILED.code == 40003
        
        assert ErrorCode.DATABASE_ERROR.code == 50001
        assert ErrorCode.INTERNAL_SERVER_ERROR.code == 50004
    
    def test_error_code_ranges(self):
        """测试错误码范围是否正确"""
        for error_code in ErrorCode:
            code = error_code.code
            
            if 10000 <= code <= 10999:
                # 通用错误范围
                assert True
            elif 20000 <= code <= 20999:
                # 数据集错误范围
                assert True
            elif 30000 <= code <= 30999:
                # 训练错误范围
                assert True
            elif 40000 <= code <= 40999:
                # 模型预测错误范围
                assert True
            elif 50000 <= code <= 50999:
                # 系统服务错误范围
                assert True
            else:
                pytest.fail(f"错误码 {code} 不在预定义范围内")


class TestDecoratorFunctionality:
    """装饰器功能测试类"""
    
    @patch.object(dataset_service, 'get_all_datasets')
    def test_standardized_response_decorator(self, mock_get_datasets):
        """测试标准化响应装饰器"""
        # Mock返回简单数据
        mock_get_datasets.return_value = [{"id": 1, "name": "test"}]
        
        response = client.get("/api/datasets")
        assert response.status_code == 200
        
        data = response.json()
        # 验证装饰器自动包装了响应
        assert data["success"] is True
        assert data["code"] == 200
        assert "获取数据集列表成功" in data["message"]
        assert isinstance(data["data"], list)
    
    @patch.object(dataset_service, 'get_all_datasets')
    def test_exception_decorator_handling(self, mock_get_datasets):
        """测试装饰器异常处理"""
        # Mock抛出异常
        mock_get_datasets.side_effect = ValueError("测试异常")
        
        response = client.get("/api/datasets")
        assert response.status_code == 500
        
        data = response.json()
        # 验证装饰器自动处理了异常
        assert data["success"] is False
        assert data["code"] == ErrorCode.INTERNAL_SERVER_ERROR.code

    def test_training_jobs_endpoint_format(self):
        """测试训练任务列表端点响应格式"""
        with patch.object(TrainingService, 'get_all_training_jobs') as mock_get_jobs:
            # Mock数据
            mock_get_jobs.return_value = [
                {
                    "id": 1,
                    "dataset_id": 1,
                    "status": "running",
                    "progress": 50,
                    "model_path": "/path/to/model"
                }
            ]
            
            response = client.get("/api/train/jobs")
            assert response.status_code == 200
            
            data = response.json()
            # 验证标准响应格式
            assert "success" in data
            assert "code" in data
            assert "message" in data
            assert "data" in data
            
            assert data["success"] is True
            assert data["code"] == 200
            assert isinstance(data["data"], list)

    def test_training_status_endpoint_format(self):
        """测试训练状态端点响应格式"""
        with patch.object(TrainingService, 'get_training_status') as mock_get_status:
            # Mock数据
            mock_get_status.return_value = {
                "job_id": 1,
                "status": "running",
                "progress": 75,
                "current_epoch": 3,
                "total_epochs": 4
            }
            
            response = client.get("/api/train/status/1")
            assert response.status_code == 200
            
            data = response.json()
            # 验证标准响应格式
            assert "success" in data
            assert "code" in data
            assert "message" in data
            assert "data" in data
            
            assert data["success"] is True
            assert data["code"] == 200
            assert isinstance(data["data"], dict)

    def test_prediction_endpoint_format(self):
        """测试预测端点响应格式"""
        with patch.object(PredictionService, 'predict') as mock_predict:
            # Mock数据
            mock_predict.return_value = {
                "prediction": "positive",
                "confidence": 0.95,
                "probabilities": {"positive": 0.95, "negative": 0.05}
            }
            
            response = client.post("/api/predict", json={"text": "test text"})
            assert response.status_code == 200
            
            data = response.json()
            # 验证标准响应格式
            assert "success" in data
            assert "code" in data
            assert "message" in data
            assert "data" in data
            
            assert data["success"] is True
            assert data["code"] == 200
            assert isinstance(data["data"], dict)