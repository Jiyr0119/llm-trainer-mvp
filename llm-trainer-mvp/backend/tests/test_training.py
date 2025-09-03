import pytest
from fastapi.testclient import TestClient
from app.models import DatasetORM, TrainingJobORM

@pytest.fixture
def sample_dataset(test_db_session):
    """创建一个示例数据集用于测试"""
    dataset = DatasetORM(
        name="test_dataset.csv",
        file_path="/tmp/test_dataset.csv",
        row_count=100,
        columns=["text", "label"],
        description="Test dataset for training"
    )
    test_db_session.add(dataset)
    test_db_session.commit()
    test_db_session.refresh(dataset)
    return dataset

def test_start_training(client, sample_dataset):
    """测试开始训练API"""
    training_params = {
        "dataset_id": str(sample_dataset.id),
        "model_name": "bert-base-chinese",
        "epochs": 3,
        "batch_size": 16,
        "learning_rate": 2e-5,
        "description": "Test training job"
    }
    
    response = client.post("/api/train/start", json=training_params)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "id" in data["data"]
    assert "status" in data["data"]
    assert data["data"]["status"] == "queued" or data["data"]["status"] == "running"

def test_get_training_jobs(client, test_db_session, sample_dataset):
    """测试获取训练任务列表API"""
    # 添加测试数据
    job1 = TrainingJobORM(
        dataset_id=sample_dataset.id,
        model_name="bert-base-chinese",
        epochs=3,
        batch_size=16,
        learning_rate=2e-5,
        status="completed",
        description="Test job 1"
    )
    job2 = TrainingJobORM(
        dataset_id=sample_dataset.id,
        model_name="bert-base-chinese",
        epochs=5,
        batch_size=32,
        learning_rate=3e-5,
        status="running",
        description="Test job 2"
    )
    test_db_session.add(job1)
    test_db_session.add(job2)
    test_db_session.commit()
    
    # 测试API
    response = client.get("/api/train/jobs")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert len(data["data"]) == 2
    assert data["data"][0]["status"] == "completed"
    assert data["data"][1]["status"] == "running"

def test_get_training_job_by_id(client, test_db_session, sample_dataset):
    """测试通过ID获取训练任务API"""
    # 添加测试数据
    job = TrainingJobORM(
        dataset_id=sample_dataset.id,
        model_name="bert-base-chinese",
        epochs=3,
        batch_size=16,
        learning_rate=2e-5,
        status="completed",
        description="Test job"
    )
    test_db_session.add(job)
    test_db_session.commit()
    test_db_session.refresh(job)
    
    # 测试API
    response = client.get(f"/api/train/jobs/{job.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["data"]["id"] == str(job.id)
    assert data["data"]["status"] == "completed"

def test_invalid_training_params(client, sample_dataset):
    """测试无效训练参数API"""
    # 缺少必要参数
    training_params = {
        "dataset_id": str(sample_dataset.id),
        # 缺少model_name
        "epochs": 3,
        "batch_size": 16
    }
    
    response = client.post("/api/train/start", json=training_params)
    
    assert response.status_code == 422  # 验证错误
    data = response.json()
    assert "detail" in data  # FastAPI验证错误格式