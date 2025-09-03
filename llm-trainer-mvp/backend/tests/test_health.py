import pytest
from fastapi.testclient import TestClient

def test_health_check(client):
    """测试健康检查API"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "status" in data["data"]
    assert data["data"]["status"] == "ok"
    assert "version" in data["data"]
    assert "environment" in data["data"]