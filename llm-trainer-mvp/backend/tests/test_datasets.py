import pytest
import io
import pandas as pd
from fastapi.testclient import TestClient
from app.models import DatasetORM

@pytest.fixture
def sample_csv_file():
    """创建一个示例CSV文件用于测试"""
    content = "text,label\nsample text 1,0\nsample text 2,1\nsample text 3,0"
    return io.BytesIO(content.encode())

def test_upload_dataset(client, sample_csv_file):
    """测试上传数据集API"""
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("test_dataset.csv", sample_csv_file, "text/csv")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "id" in data["data"]
    assert "name" in data["data"]
    assert data["data"]["name"] == "test_dataset.csv"
    assert "row_count" in data["data"]
    assert data["data"]["row_count"] == 3

def test_get_datasets(client, test_db_session):
    """测试获取数据集列表API"""
    # 添加测试数据
    dataset1 = DatasetORM(
        name="test_dataset_1.csv",
        file_path="/tmp/test_dataset_1.csv",
        row_count=10,
        columns=["text", "label"],
        description="Test dataset 1"
    )
    dataset2 = DatasetORM(
        name="test_dataset_2.csv",
        file_path="/tmp/test_dataset_2.csv",
        row_count=20,
        columns=["text", "label"],
        description="Test dataset 2"
    )
    test_db_session.add(dataset1)
    test_db_session.add(dataset2)
    test_db_session.commit()
    
    # 测试API
    response = client.get("/api/datasets")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert len(data["data"]) == 2
    assert data["data"][0]["name"] == "test_dataset_1.csv"
    assert data["data"][1]["name"] == "test_dataset_2.csv"

def test_get_dataset_by_id(client, test_db_session):
    """测试通过ID获取数据集API"""
    # 添加测试数据
    dataset = DatasetORM(
        name="test_dataset.csv",
        file_path="/tmp/test_dataset.csv",
        row_count=10,
        columns=["text", "label"],
        description="Test dataset"
    )
    test_db_session.add(dataset)
    test_db_session.commit()
    test_db_session.refresh(dataset)
    
    # 测试API
    response = client.get(f"/api/datasets/{dataset.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["data"]["id"] == str(dataset.id)
    assert data["data"]["name"] == "test_dataset.csv"

def test_get_dataset_not_found(client):
    """测试获取不存在的数据集API"""
    response = client.get("/api/datasets/999999")
    
    assert response.status_code == 404
    data = response.json()
    assert data["success"] == False
    assert "message" in data